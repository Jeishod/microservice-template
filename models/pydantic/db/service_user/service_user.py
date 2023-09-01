from uuid import UUID

from models.enum.roles import ServiceRole
from models.enum.service import Service
from models.pydantic.base import UUIDModel


class ServiceUserModel(UUIDModel):
    """Service user model"""

    service: Service
    project_user_id: UUID
    role: ServiceRole
