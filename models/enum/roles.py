from enum import StrEnum


class ProjectRole(StrEnum):
    """Project role"""

    owner = "owner"
    admin = "admin"
    user = "user"


class ServiceRole(StrEnum):
    """Service role"""

    read = "read"
    write = "write"
    comment = "comment"
