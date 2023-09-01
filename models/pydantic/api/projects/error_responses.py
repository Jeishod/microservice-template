from pydantic import (
    BaseModel,
    Field,
)


class ProjectNotFoundModel(BaseModel):
    """Not found model (404)"""

    detail: str = Field(default="Project not found: project_id=UUID('1b53f3f9-7045-4eb7-aaf9-3d49ec84c021')")
