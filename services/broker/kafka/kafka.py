import asyncio
import logging
import time
from collections import namedtuple
from functools import wraps
from typing import (
    Awaitable,
    Callable,
    Coroutine,
    Optional,
    get_args,
)

import aiokafka
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    avro,
)
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    SerializationError,
)
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from starlette import status

from services.broker import (
    Broker,
    DeserializationError,
)
from services.metrics import Collector


CallbackType = Callable[[BaseModel | list[BaseModel]], Awaitable[None]]


class KafkaBroker(Broker):
    """
    Complex kafka operations
    """

    TopicKey = namedtuple("TopicKey", "topic key")
    _serializers_cache: dict[str, avro.AvroSerializer] = {}
    _batch_callbacks: dict[TopicKey, asyncio.Queue] = {}
    _tasks: list[Coroutine] = []
    _collector: Collector
    _deserializer: avro.AvroDeserializer
    producer: aiokafka.AIOKafkaProducer | None
    consumer: aiokafka.AIOKafkaConsumer | None

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        collector: Collector,
        schema_registry_configuration: dict,
    ) -> None:
        self.schema_registry_client: SchemaRegistryClient = SchemaRegistryClient(conf=schema_registry_configuration)
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self.__class__._collector = collector
        self.__class__._deserializer = avro.AvroDeserializer(schema_registry_client=self.schema_registry_client)
        self.__class__.producer = None
        self.__class__.consumer = None

    @classmethod
    def listen(
        # fmt: off
        cls,
        topic: str,
        key: Optional[str] = None,
        messages_count: int = 1,
        interval_period_sec: float = 1.0,
        # fmt: on
    ) -> Callable:
        """Decorator maker.

        Needed only to receive message processing arguments.

        Args:
            topic: Kafka topic name
            key: message key from Kafka
            messages_count: buffer size for accumulating messages from Kafka
            interval_period_sec: number of seconds to fill the buffer

        Returns:
            Decorator object
        """

        def inner(function: CallbackType) -> CallbackType:
            """Decorator.

            Prepares a mapping of the topic name and the function to which the deserialized messages should be returned.

            Args:
                function: function to which the deserialized messages should be returned

            Returns:
                Wrapper above the function
            """

            @wraps(function)
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)

            first_arg_type = next(iter(wrapper.__annotations__.values()))
            callback_key = cls.make_key(topic=topic, key=key)
            is_multiple = len(get_args(first_arg_type)) > 0
            model = get_args(first_arg_type)[0] if is_multiple else first_arg_type
            async_queue: asyncio.Queue = asyncio.Queue()
            cls._batch_callbacks[callback_key] = async_queue
            cls._tasks.append(
                cls.capacitor(
                    topic_key=callback_key,
                    async_queue=async_queue,
                    function=function,
                    model=model,
                    max_buffer_size=messages_count,
                    interval_period_sec=interval_period_sec,
                    is_multiple=is_multiple,
                )
            )
            return wrapper

        return inner

    @staticmethod
    def make_key(topic: str, key: bytes | str | None) -> TopicKey:
        """Makes a keychain with topic name and message key.

        Args:
            topic: Kafka topic name
            key: message key from Kafka

        Returns:
            Namedtuple Topic with keychain: topic name and message key
        """
        prepared_key = key.encode() if isinstance(key, str) else key
        return KafkaBroker.TopicKey(topic=topic, key=prepared_key)

    @classmethod
    def prepare_obj(cls, src_object: aiokafka.structs.ConsumerRecord, target_model: BaseModel) -> BaseModel:
        """Deserializes object to decorated function argument.

        Args:
            src_object: Kafka message to deserialize
            target_model: decorated function argument to which to deserialize

        Returns:
            Deserialized object
        """
        try:
            deserialized_obj: object = cls._deserializer(
                data=src_object.value,
                ctx=SerializationContext(src_object.topic, MessageField.VALUE),
            )
        except SerializationError:
            logging.exception(f"Deserialization error with {src_object=}")
            raise

        return target_model.parse_obj(deserialized_obj)

    async def start(self) -> None:
        """Starts process of multiple writing Kafka messages to asynchronous queues."""
        topics = [key.topic for key in self._batch_callbacks]
        if not topics:
            return

        self.__class__.producer = aiokafka.AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self.__class__.producer.start()

        consumer = aiokafka.AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        self.__class__.consumer = consumer
        await self.__class__.consumer.start()

        asyncio.gather(*self._tasks)

        try:
            async for msg in consumer:
                callback_key = self.make_key(topic=msg.topic, key=msg.key)
                if callback_key not in self._batch_callbacks:
                    continue
                target_queue = self._batch_callbacks[callback_key]
                await target_queue.put(msg)
        except aiokafka.errors.ConsumerStoppedError:
            pass
        finally:
            logging.info("Stopping consumer")
            if self.consumer:
                await self.consumer.stop()

    async def stop(self) -> None:
        """Stop process consumer"""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

    @classmethod
    async def _process_and_clear_buffer(
        cls,
        buffer: list,
        topic: str,
        key: str | None,
        model: BaseModel,
        is_multiple: bool,
        function: CallbackType,
    ) -> None:
        """
        Processing accumulated messages and corresponding call

        Args:
            buffer: container with messages to process
            topic: single topic name
            key: corrected kafka key
            model: decorated function argument to which to deserialize
            is_multiple: flag, that indicates type of function arguments
            function: function to which the deserialized messages should be returned
        """
        cls._collector.increment_consumer_total(topic=topic, key=key, count=len(buffer))
        prepared_objs = []
        topics = {}
        for consumer_message in buffer:
            try:
                prepared_obj: BaseModel = cls.prepare_obj(
                    src_object=consumer_message,
                    target_model=model,
                )
                prepared_objs.append(prepared_obj)
                topic_partition = aiokafka.TopicPartition(consumer_message.topic, consumer_message.partition)
                topics[topic_partition] = consumer_message.offset + 1
            except DeserializationError as deserialization_error:
                logging.exception(deserialization_error)
                cls._collector.increment_consumer_error(topic=topic, key=key)
                raise

        if prepared_objs:
            if is_multiple:
                await function(prepared_objs)
            else:
                await function(prepared_objs[0])

        if topics:
            await cls.consumer.commit(topics)

        buffer.clear()

    @classmethod
    async def capacitor(  # pylint: disable=too-many-arguments
        cls,
        topic_key: TopicKey,
        async_queue: asyncio.Queue,
        function: CallbackType,
        model: BaseModel,
        max_buffer_size: int,
        interval_period_sec: float,
        is_multiple: bool,
    ):
        """Reads Kafka messages from asynchronous queues and gives them to decorated functions.

        Args:
            topic_key: Kafka topic name with key
            async_queue: asynchronous queue to read messages
            function: function to which the deserialized messages should be returned
            model: decorated function argument to which to deserialize
            max_buffer_size: buffer size for accumulating messages from Kafka
            interval_period_sec: number of seconds to fill the buffer
            is_multiple: flag, that indicates type of function arguments
        """
        key = topic_key.key.decode() if topic_key.key else None
        time_inner = interval_period_sec
        buffer = []
        while True:
            try:
                start_time = time.monotonic()
                message = await asyncio.wait_for(async_queue.get(), time_inner)
                buffer.append(message)

                if len(buffer) >= max_buffer_size:
                    raise asyncio.TimeoutError

                time_inner -= time.monotonic() - start_time
            except asyncio.TimeoutError:
                if buffer:
                    try:
                        await cls._process_and_clear_buffer(
                            buffer=buffer,
                            topic=topic_key.topic,
                            key=key,
                            model=model,
                            is_multiple=is_multiple,
                            function=function,
                        )
                    except Exception as exception:
                        cls._collector.increment_consumer_processing_error(topic=topic_key.topic, key=key)
                        logging.error(f"Consumer stopped: {topic_key=}")
                        logging.exception(exception)
                        break

                time_inner = interval_period_sec

            except asyncio.exceptions.CancelledError:
                return

    async def produce(self, topic: str, message: BaseModel, key: str | None = None) -> None:
        """
        Produce message to topic

        Args:
            topic: kafka topic
            key: topic key
            message: bytes serializable value
        """
        if not self.producer:
            raise ConnectionError("Producer not initialized")

        serializer = self._get_serializer(topic=topic)

        try:
            serialized_message = serializer(message.dict(), SerializationContext(topic, MessageField.VALUE))
        except TypeError as type_error:
            error_message: str = f"Incorrect schema: {serializer._parsed_schema=}, {topic=}, {message=}"
            logging.error(error_message)
            raise HTTPException(status_code=status.HTTP_426_UPGRADE_REQUIRED, detail=error_message) from type_error

        await self.producer.send(
            topic=topic,
            value=serialized_message,
            key=key,
        )

    def _get_serializer(
        self,
        topic: str,
    ) -> avro.AvroSerializer:
        """
        Gets the latest version schema

        Args:
            topic: kafka topic

        Returns:
            Latest version serializer
        """
        if topic not in self._serializers_cache:
            schema = self.schema_registry_client.get_latest_version(topic).schema
            serializer = avro.AvroSerializer(
                schema_registry_client=self.schema_registry_client,
                schema_str=schema,
            )
            self.__class__._serializers_cache[topic] = serializer
        else:
            serializer = self._serializers_cache[topic]

        return serializer
