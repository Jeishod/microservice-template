from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from models.enum import Service
from services.broker.kafka.settings import KafkaSettings
from services.database.postgresql.postgresql import PostgreSQLParams
from services.s3_storage import (
    MinioParams,
    S3Params,
)
from services.storage_orm import RedisORMParams


class Settings(BaseSettings):
    """General service settings"""

    DEBUG: int = Field(default=0)

    APP_TITLE: str = "Microservice template"
    APP_DESCRIPTION: str = "Example of microservice"

    LOG_FORMAT: str = "%(asctime)s [%(name)s:%(lineno)s] [%(levelname)s]: %(message)s"

    postgresql: PostgreSQLParams = PostgreSQLParams()
    kafka_settings: KafkaSettings = KafkaSettings()
    redis: RedisORMParams = RedisORMParams()
    minio: MinioParams = MinioParams()
    s3: S3Params = S3Params()

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_")


class ConstSettings:
    """Constant settings"""

    SERVICE = Service.template
