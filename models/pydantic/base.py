import uuid
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_serializer,
    model_validator,
)
from sqlalchemy import Row

from models.sqlalchemy.base import SqlAlchemyBase


class SerializedModel(BaseModel, use_enum_values=True):
    """Base model with UUID and Enum serialization."""

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """Serialize UUIDs and enums to strings.

        Returns:
            dict[str, Any]: serialized model
        """
        model: dict[str, Any] = {}
        for attr, value in self.__dict__.items():
            if isinstance(value, uuid.UUID):
                value = str(value)
            model[attr] = value
        return model


class OrmModel(SerializedModel):
    """ORM model with SQLAlchemy (both ORM and Core) query result mapping to Pydantic model via `.model_validate()`."""

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def load_object(cls, obj: SqlAlchemyBase | Row | BaseModel | dict) -> dict[str, Any]:
        """Prepare object for valid Pydantic attributes mapping via `.model_validate()`.

        Args:
            obj (SqlAlchemyBase | Row | BaseModel | dict): object to load in Pydantic model.
                1. SqlAlchemyBase - if object is SqlAlchemy ORM model
                2. Row - if object is SqlAlchemy Core query result
                3. BaseModel - if model is created from another Pydantic model.
                4. Dict - if model is created in a usual way via attributes.

        Returns:
            dict[str, Any]: prepared dict to load into Pydantic model
        """
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        parsed: dict[str, Any] = {}
        if isinstance(obj, SqlAlchemyBase):
            parsed.update(obj.__dict__)
            return parsed
        for field, value in obj._asdict().items():
            if isinstance(value, SqlAlchemyBase):
                parsed.update(value.__dict__)
            else:
                parsed[field] = value
        return parsed


class UUIDModel(OrmModel):
    """ORM model with automatic UUID generator for `id` field."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
