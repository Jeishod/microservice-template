from sqlalchemy import (
    UUID,
    Column,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import Mapped

from models.enum.roles import ServiceRole
from models.enum.service import Service
from models.sqlalchemy.base import SqlAlchemyBase


class ServiceUsers(SqlAlchemyBase):
    """Service user ORM model"""

    __tablename__ = "service_users"

    id: Mapped[UUID] = Column(UUID, primary_key=True)
    service: Mapped[Service] = Column(
        Enum(Service, values_callable=lambda x: [e.value for e in Service]),
        nullable=False,
        unique=True,
    )
    project_user_id: Mapped[UUID] = Column(UUID, ForeignKey("project_users.id", ondelete="cascade"), nullable=False)
    role: Mapped[ServiceRole] = Column(
        Enum(ServiceRole, values_callable=lambda x: [e.value for e in ServiceRole]),
        nullable=False,
        server_default=ServiceRole.read.value,
    )
