from enum import StrEnum


class CollectorObjectType(StrEnum):
    """Types of objects collected by the collector"""

    TOTAL = "total"
    UNPICKLING_ERRORS = "error_bodies"
    INSERT_ERROR = "error_objects"
