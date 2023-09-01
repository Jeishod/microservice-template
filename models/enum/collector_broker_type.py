from enum import StrEnum


class CollectorConsumerType(StrEnum):
    """Types of objects collected by the collector"""

    TOTAL = "total"
    DESERIALIZATION_ERROR = "deserialization_error"
    PROCESSING_ERROR = "processing_error"


class CollectorProducerType(StrEnum):
    """Types of objects produced by the collector"""

    TOTAL = "total"
    PRODUCING_ERROR = "producing_error"
