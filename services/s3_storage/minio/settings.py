from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class MinioParams(BaseSettings):
    """RedisORM settings"""

    ENDPOINT: str = Field(default="localhost:9000")
    ACCESS_KEY: str = Field(default="")
    SECRET_KEY: str = Field(default="")
    SECURE: bool = False
    BUCKET: str = Field(default="bucket")

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_S3_")
