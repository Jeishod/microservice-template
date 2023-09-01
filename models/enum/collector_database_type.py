from enum import StrEnum


class CollectorDatabaseType(StrEnum):
    """Types of objects collected by the collector"""

    TOTAL_CREATED = "total_created"
    ERROR_CREATION = "error_creation"
