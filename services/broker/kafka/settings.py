from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class KafkaSettings(BaseSettings):
    """Kafka broker settings"""

    BOOTSTRAP_SERVERS: str = Field(default="localhost:39092")
    GROUP_ID: str = Field(default="")

    ENCODING_TYPE: str = Field(default="utf-8")

    SCHEMA_REGISTRY_URL: str = Field(default="http://localhost:8085")

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_KAFKA_")

    @property
    def schema_registry_configuration(self):
        return {"url": f"{self.SCHEMA_REGISTRY_URL}"}
