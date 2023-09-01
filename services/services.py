import asyncio
import logging

from aiostorage_orm import (
    AIORedisORM,
    AIOStorageORM,
)
from minio import Minio

from app.settings import Settings
from services.broker import (
    Broker,
    KafkaBroker,
)
from services.database import (
    Database,
    PostgreSQL,
)
from services.metrics import Collector


class Services:
    """Service Orchestrator"""

    config: Settings = Settings()

    collector: Collector = Collector()

    pg_echo_pool = "debug" if config.postgresql.ECHO_POOL else False
    database: Database = PostgreSQL(params=config.postgresql)
    broker: Broker = KafkaBroker(
        bootstrap_servers=config.kafka_settings.BOOTSTRAP_SERVERS,
        group_id=config.kafka_settings.GROUP_ID,
        collector=collector,
        schema_registry_configuration=config.kafka_settings.schema_registry_configuration,
    )
    storage_orm: AIOStorageORM = AIORedisORM(
        host=config.redis.HOST,
        port=config.redis.PORT,
        db=config.redis.DB,
    )
    minio: Minio = Minio(
        endpoint=config.minio.ENDPOINT,
        access_key=config.minio.ACCESS_KEY,
        secret_key=config.minio.SECRET_KEY,
        secure=config.minio.SECURE,
    )

    def set_logging_config(self):
        """Уровень логирования, в зависимости от режима DEBUG"""
        logging_level = "DEBUG" if self.config.DEBUG else "INFO"
        logging_format = "%(asctime)s [%(name)s:%(lineno)s] [%(levelname)s]: %(message)s"
        logging.basicConfig(level=logging_level, format=logging_format)

    async def initialize_services(self) -> None:
        """Perform initialization operations. Including making connections"""
        self.set_logging_config()
        self.collector.initialize()

    async def initialize_db(self) -> None:
        """Perform initialization operations. Including making connections"""
        await self.database.connect()

    async def initialize_broker(self) -> None:
        """Perform initialization operations. Including making connections"""
        asyncio.create_task(self.broker.start())

    async def initialize_cache(self) -> None:
        """Perform initialization operations. Including making connections"""
        await self.storage_orm.init()

    async def initialize_s3(self) -> None:
        """Perform initialization operations. Including making connections"""
        self.minio = Minio(
            endpoint=self.config.minio.ENDPOINT,
            access_key=self.config.minio.ACCESS_KEY,
            secret_key=self.config.minio.SECRET_KEY,
            secure=self.config.minio.SECURE,
        )
        if not self.minio.bucket_exists(self.config.minio.BUCKET):
            self.minio.make_bucket(self.config.minio.BUCKET)

    async def stop_broker(self) -> None:
        """Perform stop operations"""
        await self.broker.stop()
