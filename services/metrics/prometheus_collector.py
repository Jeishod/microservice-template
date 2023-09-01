import prometheus_client

from models import enum
from models.sqlalchemy.base import SqlAlchemyBase


class Collector:
    """Mechanism for collecting statistics"""

    db_objects: prometheus_client.Counter  # Metrics for objects created in the database
    consumer_objects: prometheus_client.Counter  # Metrics for objects created in the database

    def initialize(self) -> None:
        """
        Creating counters
            - statistics query example in prometheus:
                increase(processed_objects_total[5s])
            labels for type: models.CollectorObjectType
        """
        self.consumer_objects = prometheus_client.Counter(
            "consumer_objects",
            "Consumer processing results",
            labelnames=["type"],
        )
        self.db_objects = prometheus_client.Counter(
            "database_objects",
            "Database models processing",
            labelnames=["type"],
        )

    def increment_consumer_total(self, topic: str, key: str | None, count: int = 1) -> None:
        """Adding metrics for processed data"""
        label = f"{topic}.{key}.{enum.CollectorConsumerType.TOTAL}"
        self.consumer_objects.labels(label).inc(count)

    def increment_consumer_error(self, topic: str, key: str | None) -> None:
        """Adding metrics for processed data"""
        label = f"{topic}.{key}.{enum.CollectorConsumerType.DESERIALIZATION_ERROR}"
        self.consumer_objects.labels(label).inc()

    def increment_consumer_processing_error(self, topic: str, key: str | None) -> None:
        """Adding metrics for processed data"""
        label = f"{topic}.{key}.{enum.CollectorConsumerType.PROCESSING_ERROR}"
        self.consumer_objects.labels(label).inc()

    def increment_database_total(self, model: SqlAlchemyBase) -> None:
        """DB creations counter"""
        label = f"{model.__tablename__}.{enum.CollectorDatabaseType.TOTAL_CREATED}"
        self.db_objects.labels(label).inc()

    def increment_database_error(self, model: SqlAlchemyBase) -> None:
        """DB error creations counter"""
        label = f"{model.__tablename__}.{enum.CollectorDatabaseType.ERROR_CREATION}"
        self.db_objects.labels(label).inc()

    def generate(self) -> bytes:
        """Forwarding the generation of statistics results"""
        return prometheus_client.generate_latest()
