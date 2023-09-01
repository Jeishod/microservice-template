from uuid import UUID

from sqlalchemy import (
    and_,
    exists,
    select,
)

from app.db.db_base import DatabaseBase
from app.settings import ConstSettings
from models.pydantic.db.user import (
    UserExtended,
    UserModel,
)
from models.sqlalchemy import (
    Projects,
    ProjectUsers,
    ServiceUsers,
    Users,
)
from services import Services


class UserDb(DatabaseBase):
    """Working with users"""

    async def create(self, user: UserModel) -> UserModel:
        """Create user.

        Args:
            user (UserModel): user model

        Returns:
            UserModel: created user model
        """
        user_db = Users(**user.model_dump())
        async with Services.database.session() as session:
            session.add(user_db)
            Services.collector.increment_database_total(model=user_db)
        return UserModel.model_validate(user_db)

    async def get(self, user_id: UUID) -> UserModel | None:
        """Get user by its ID.

        Args:
            user_id (UUID): user ID

        Returns:
            UserModel | None: user model if found, None otherwise
        """
        query = select(Users).where(Users.id == user_id)
        async with Services.database.session() as session:
            result = await session.execute(query)
        user = result.fetchone()
        if not user:
            return None
        return UserModel.model_validate(user)

    async def get_by_email(self, email: str) -> UserModel | None:
        """Get user by email.

        Args:
            email (str): user email

        Returns:
            UserModel | None: user model if found, None otherwise
        """
        query = select(Users).where(Users.email == email)
        async with Services.database.session() as session:
            result = await session.execute(query)
        user = result.fetchone()
        if not user:
            return None
        return UserModel.model_validate(user)

    async def get_extended_by_email(self, email: str, project_id: UUID) -> UserExtended | None:
        """Get user within project and service with its roles by user email.

        Args:
            email (str): user email
            project_id (UUID): project ID

        Returns:
            UserExtended | None: user model if found, None otherwise
        """
        query = (
            select(
                Users,
                ProjectUsers.id.label("project_user_id"),
                ProjectUsers.role.label("project_role"),
                ServiceUsers.id.label("service_user_id"),
                ServiceUsers.role.label("service_role"),
                Projects.id.label("project_id"),
                Projects.name.label("project_name"),
                Projects.description.label("project_description"),
            )
            .join(ProjectUsers, ProjectUsers.user_id == Users.id)
            .join(ServiceUsers, ServiceUsers.project_user_id == ProjectUsers.id)
            .join(Projects, Projects.id == ProjectUsers.project_id)
            .where(and_(Users.email == email, Projects.id == project_id, ServiceUsers.service == ConstSettings.SERVICE))
        )
        async with Services.database.session() as session:
            result = await session.execute(query)
        user = result.fetchone()
        if not user:
            return None
        return UserExtended.model_validate(user)

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email.

        Args:
            email (str): user email

        Returns:
            bool: True if user exists, False otherwise
        """
        query = exists(Users).where(Users.email == email).select()
        async with Services.database.session() as session:
            result = await session.execute(query)
        return bool(result.scalar())
