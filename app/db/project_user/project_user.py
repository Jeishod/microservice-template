from app.db.db_base import DatabaseBase
from models.pydantic.db import ProjectUserModel
from models.sqlalchemy import ProjectUsers
from services import Services


class ProjectUserDb(DatabaseBase):
    """Working with project users"""

    async def create(self, project_user: ProjectUserModel) -> ProjectUserModel:
        """Create project user.

        Args:
            project_user (ProjectUserModel): project user model

        Returns:
            ProjectUserModel: created project user
        """
        project_user_db = ProjectUsers(**project_user.model_dump())
        async with Services.database.session() as session:
            session.add(project_user_db)
            Services.collector.increment_database_total(model=project_user_db)
        return ProjectUserModel.model_validate(project_user_db)
