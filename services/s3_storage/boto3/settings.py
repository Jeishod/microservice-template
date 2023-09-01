from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class S3Params(BaseSettings):
    """S3 storage settings"""

    ENDPOINT: str = Field(default="localhost:4566")
    ACCESS_KEY: str = Field(default="")
    SECRET_KEY: str = Field(default="")
    DEFAULT_BUCKET: str = Field(default="")
    SECURE: bool = False

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_S3_")
