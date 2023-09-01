from uuid import UUID

from models.enum import (
    ProjectRole,
    ServiceRole,
)
from models.pydantic.base import UUIDModel


class UserModel(UUIDModel):
    """User model"""

    email: str
    name: str
    password: str | None = None


class UserWithPassword(UserModel):
    """User model with mandatory password"""

    password: str


class UserExtended(UserModel):
    """User with its project and service info"""

    project_user_id: UUID
    project_id: UUID
    project_name: str
    project_description: str | None = None
    project_role: ProjectRole
    service_user_id: UUID
    service_role: ServiceRole
