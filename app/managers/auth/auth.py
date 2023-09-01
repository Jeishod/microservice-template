from app.auth import auth_manager
from app.db import Database
from app.managers.managers_base import ManagersBase
from models import pydantic


class AuthManager(ManagersBase):
    """Authorization manager"""

    async def register(self, user_info: pydantic.PostRegisterRequest) -> pydantic.PostRegisterResponse:
        """Logic of endpoint POST `/auth/register`

        Args:
            user_info (pydantic.PostRegisterRequest): info about the user to create

        Raises:
            pydantic.ObjectAlreadyExists: if user with such email already exists

        Returns:
            pydantic.PostRegisterResponse: registered user
        """
        user_existing = await Database.users.exists_by_email(email=user_info.email)
        if user_existing:
            raise pydantic.ObjectAlreadyExists(
                message_prefix="User with such email already exists.", email=user_info.email
            )
        plain_password = user_info.password
        user_info.password = auth_manager.get_password_hash(password=user_info.password)
        user_model = pydantic.UserModel.model_validate(user_info)
        user = await Database.users.create(user=user_model)
        return pydantic.PostRegisterResponse(id=user.id, email=user.email, name=user.name, password=plain_password)

    async def login(self, username: str, password: str) -> pydantic.PostLoginResponse:
        """Logic of endpoint POST `/auth/jwt/login`

        Args:
            username (str): user email
            password (str): user password

        Raises:
            pydantic.AuthenticationFailed: if user is not found by email or password is invalid

        Returns:
            pydantic.PostLoginResponse: access token
        """
        user = await Database.users.get_by_email(email=username)
        if not user:
            raise pydantic.AuthenticationFailed()
        if not user.password:
            raise pydantic.UserHasNoPassword()
        if not auth_manager.verify_password(plain_password=password, hashed_password=user.password):
            raise pydantic.AuthenticationFailed()
        access_token = auth_manager.create_access_token(email=user.email)
        return pydantic.PostLoginResponse(access_token=access_token)
