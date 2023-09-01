import uuid

from sqlalchemy import select

from app.db.db_base import DatabaseBase
from models.pydantic.db.project import ProjectModel
from models.sqlalchemy import Projects
from services import Services


class ProjectDb(DatabaseBase):
    """Working with projects"""

    async def create(self, project_model: ProjectModel) -> ProjectModel:
        """Create project.

        Args:
            project_model (ProjectModel): project model

        Returns:
            ProjectModel: created project model
        """
        project_db = Projects(**project_model.model_dump())
        async with Services.database.session() as session:
            session.add(project_db)
            Services.collector.increment_database_total(model=project_db)
        return ProjectModel.model_validate(project_db)

    async def get(self, project_id: uuid.UUID) -> ProjectModel | None:
        """Get project by its ID.

        Args:
            project_id (uuid.UUID): project ID

        Returns:
            ProjectModel | None: project model if found, None otherwise
        """
        query = select(Projects).where(Projects.id == project_id)
        async with Services.database.session() as session:
            result = await session.execute(query)
        project = result.fetchone()
        if not project:
            return None
        return ProjectModel.model_validate(project)
