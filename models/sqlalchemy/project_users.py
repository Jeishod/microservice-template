from sqlalchemy import (
    UUID,
    Column,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import Mapped

from models.enum.roles import ProjectRole
from models.sqlalchemy.base import SqlAlchemyBase


class ProjectUsers(SqlAlchemyBase):
    """Project user ORM model"""

    __tablename__ = "project_users"

    id: Mapped[UUID] = Column(UUID, primary_key=True)
    project_id: Mapped[UUID] = Column(UUID, ForeignKey("projects.id", ondelete="cascade"), nullable=False)
    user_id: Mapped[UUID] = Column(UUID, ForeignKey("users.id", ondelete="cascade"), nullable=False)
    role: Mapped[ProjectRole] = Column(
        Enum(ProjectRole, values_callable=lambda x: [e.value for e in ProjectRole]),
        nullable=False,
        server_default=ProjectRole.user.value,
    )
