from typing import Literal

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class PostgreSQLParams(BaseSettings):
    """Database service settings"""

    HOST: str = Field(default="localhost")
    PORT: int = Field(default=5432)
    USERNAME: str = Field(default="cyberdev")
    PASSWORD: str = Field(default="cyberdev")
    DATABASE: str = Field(default="cyberdev")
    ECHO_POOL: Literal["debug"] | bool = Field(default=False)  # "DEBUG"\False
    POOL_SIZE: int = Field(default=10)
    CONNECTION_RETRY_PERIOD_SEC: float = Field(default=5.0)

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_DB_")
