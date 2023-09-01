from datetime import datetime

from models.pydantic.base import SerializedModel


class JwtPayload(SerializedModel):
    email: str
    exp: datetime | None = None
