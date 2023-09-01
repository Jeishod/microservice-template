from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class RedisORMParams(BaseSettings):
    """RedisORM settings"""

    HOST: str = Field(default="localhost")
    PORT: int = Field(default="6379")
    DB: int = Field(default=0)

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_REDIS_ORM_")
