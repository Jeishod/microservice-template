from sqlalchemy import (
    UUID,
    Column,
    String,
)
from sqlalchemy.orm import Mapped

from models.sqlalchemy.base import SqlAlchemyBase


class Users(SqlAlchemyBase):
    """Users ORM model"""

    __tablename__ = "users"

    id: Mapped[UUID] = Column(UUID, primary_key=True)
    email: Mapped[str] = Column(String, nullable=False, index=True, unique=True)
    name: Mapped[str] = Column(String, nullable=False)
    password: Mapped[str] | None = Column(String, nullable=True)
