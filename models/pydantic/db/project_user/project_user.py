from uuid import UUID

from models.enum.roles import ProjectRole
from models.pydantic.base import UUIDModel


class ProjectUserModel(UUIDModel):
    """Project user model"""

    project_id: UUID
    user_id: UUID
    role: ProjectRole
