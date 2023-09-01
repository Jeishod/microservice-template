import logging
from datetime import (
    datetime,
    timedelta,
)

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app.auth.settings import AuthorizationSettings
from models import pydantic
from models.enum.auth import AuthFlow


class Authorization:
    """Local authorization manager."""

    logger: logging.Logger
    crypto_manager: CryptContext
    settings: AuthorizationSettings

    def __init__(self, settings: AuthorizationSettings):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings
        self.crypto_manager = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_schema = OAuth2PasswordBearer(tokenUrl=settings.LOGIN_URL)

    def get_password_hash(self, password: str) -> str:
        """Get hash of the provided password.

        Args:
            password (str): password

        Returns:
            str: password hash
        """
        return self.crypto_manager.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against given hashed password.

        Args:
            plain_password (str): unhashed password
            hashed_password (str): hashed password

        Returns:
            bool: True if passwords are verified, else False
        """
        return self.crypto_manager.verify(plain_password, hashed_password)

    def create_access_token(self, email: str, expires_delta: int | None = None) -> str:
        """Create JWT access token.

        Args:
            email (str): user email
            expires_delta (timedelta, optional): JWT token expiration time in seconds.
                If not provided - defaults to ACCESS_TOKEN_EXPIRE.

        Returns:
            str: JWT access token
        """
        if not expires_delta:
            expires_delta = self.settings.ACCESS_TOKEN_EXPIRE
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        jwt_payload = pydantic.JwtPayload(email=email, exp=expire)
        encoded_jwt = jwt.encode(
            claims=jwt_payload.model_dump(), key=self.settings.SECRET_KEY, algorithm=self.settings.PASSWORD_ALGORYTHM
        )
        return encoded_jwt

    async def decode_access_token(self, token: str) -> pydantic.JwtPayload:
        """Decode JWT access token and get JWT payload.

        Args:
            token (str): JWT access token

        Returns:
            JwtPayload: JWT payload with user ID and expiration time
        """
        if self.settings.FLOW == AuthFlow.LOCAL:
            payload = jwt.decode(token=token, key=self.settings.SECRET_KEY, algorithms=self.settings.PASSWORD_ALGORYTHM)
        else:
            decoded_payload = jwt.get_unverified_claims(token)
            oidc_user = pydantic.OIDCUser.model_validate(decoded_payload)
            payload = pydantic.JwtPayload(email=oidc_user.email)
        return pydantic.JwtPayload.model_validate(payload)


auth_manager = Authorization(settings=AuthorizationSettings())
