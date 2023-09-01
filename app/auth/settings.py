from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from models.enum import AuthFlow


class AuthorizationSettings(BaseSettings):
    """Authorization settings"""

    FLOW: AuthFlow = AuthFlow.LOCAL
    SECRET_KEY: str = Field(default="qwerty")
    PASSWORD_ALGORYTHM: str = "HS256"
    LOGIN_URL: str = "/auth/jwt/login"
    ACCESS_TOKEN_EXPIRE: int = Field(default=60 * 60 * 24 * 7 * 2)  # two weeks in seconds

    model_config = SettingsConfigDict(env_prefix="SERVICE_NAME_AUTH_")
