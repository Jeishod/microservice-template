from app.db.db_base import DatabaseBase
from models.pydantic.db import ServiceUserModel
from models.sqlalchemy import ServiceUsers
from services import Services


class ServiceUserDb(DatabaseBase):
    """Working with service users"""

    async def create(self, service_user: ServiceUserModel) -> ServiceUserModel:
        """Create service user.

        Args:
            service_user (ServiceUserModel): service user model

        Returns:
            ServiceUserModel: created service user
        """
        service_user_db = ServiceUsers(**service_user.model_dump())
        async with Services.database.session() as session:
            session.add(service_user_db)
            Services.collector.increment_database_total(model=service_user_db)
        return ServiceUserModel.model_validate(service_user_db)
