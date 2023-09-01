from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    Path,
)
from jose import JWTError

from app.auth import auth_manager
from app.db import Database
from models import pydantic
from models.enum.roles import ServiceRole


async def get_user_email(token: Annotated[str, Depends(auth_manager.oauth2_schema)]) -> str:
    """Get user email from access token.

    Args:
        token (str): access token

    Raises:
        pydantic.InvalidCredentials: if JWT token was not decoded

    Returns:
        UUID: user ID
    """
    try:
        jwt_payload = await auth_manager.decode_access_token(token=token)
    except JWTError:
        raise pydantic.InvalidCredentials()
    return jwt_payload.email


async def get_user(email: Annotated[str, Depends(get_user_email)]) -> pydantic.UserModel:
    """Get user model.

    Args:
        email (Annotated[str, Depends): user email (via access token)

    Raises:
        pydantic.ObjectNotFound: if user was not found by its email

    Returns:
        pydantic.UserModel: user model
    """
    user = await Database.users.get_by_email(email=email)
    if not user:
        raise pydantic.InvalidCredentials()
    return user


async def get_user_in_project_service(
    email: Annotated[str, Depends(get_user_email)], project_id: Annotated[UUID, Path(description="ID of project")]
) -> pydantic.UserExtended:
    """Get user within project and service.

    Args:
        email (Annotated[UUID, Depends): user email (via access token)
        project_id (Annotated[UUID, Path): project ID (via path parameter)

    Raises:
        pydantic.ObjectNotFound: if user was not found in project and service

    Returns:
        pydantic.UserExtended: user extended model (with project and service info)
    """
    user = await Database.users.get_extended_by_email(email=email, project_id=project_id)
    if not user:
        raise pydantic.InvalidCredentials()
    return user


class UserWithServiceAccess:
    """Dependency which checks if user has necessary rights for the service"""

    ALLOWED_ACTIONS = {
        ServiceRole.write: {ServiceRole.write, ServiceRole.read, ServiceRole.comment},
        ServiceRole.read: {ServiceRole.read, ServiceRole.comment},
        ServiceRole.comment: {ServiceRole.comment},
    }

    def __init__(self, scopes: list[ServiceRole]) -> None:
        self.scopes = scopes

    def __call__(
        self, user: Annotated[pydantic.UserExtended, Depends(get_user_in_project_service)]
    ) -> pydantic.UserExtended:
        for scope in self.scopes:
            if scope not in self.ALLOWED_ACTIONS[user.service_role]:
                raise pydantic.UserNoServiceRights(email=user.email, user_role=user.service_role, necessary_role=scope)
        return user
