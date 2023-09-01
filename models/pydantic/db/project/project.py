from models.pydantic.base import UUIDModel


class ProjectModel(UUIDModel):
    """Project model"""

    name: str
    description: str | None = None
