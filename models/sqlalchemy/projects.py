from sqlalchemy import (
    UUID,
    Column,
    String,
    Text,
)
from sqlalchemy.orm import Mapped

from models.sqlalchemy.base import SqlAlchemyBase


class Projects(SqlAlchemyBase):
    """Projects ORM model"""

    __tablename__ = "projects"

    id: Mapped[UUID] = Column(UUID, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
