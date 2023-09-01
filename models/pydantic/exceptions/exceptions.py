from fastapi.exceptions import HTTPException
from starlette import status

from models.enum import ServiceRole


class ObjectAlreadyExists(HTTPException):
    """Error occurs when object already exists"""

    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, message_prefix: str, **kwargs) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=f"{message_prefix}: {kwargs}",
        )


class ObjectNotFound(HTTPException):
    """Error occurs when object not found"""

    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, message_prefix: str, **kwargs) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=f"{message_prefix}: {kwargs}",
        )


class DatabaseException(HTTPException):
    """Error occurs when something go wrong in the database"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message_prefix: str = "Database error"

    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=f"{self.message_prefix}: {message}",
        )


class AuthenticationFailed(HTTPException):
    """Error occurs when user authentication has failed"""

    status_code: int = status.HTTP_401_UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail="Authenticaion failed. Please check your email and password.",
        )


class InvalidCredentials(HTTPException):
    """Error occurs when user authentication has failed"""

    status_code: int = status.HTTP_401_UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail="Could not validate credentials.",
        )


class UserHasNoPassword(HTTPException):
    """Error occurs when user is not suitable for local authorization"""

    status_code: int = status.HTTP_403_FORBIDDEN

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail="Unable to login as user not for local development",
        )


class UserNoServiceRights(HTTPException):
    """Error occurs when user has no necessary rights in the service"""

    status_code: int = status.HTTP_403_FORBIDDEN

    def __init__(self, email: str, user_role: ServiceRole, necessary_role: ServiceRole) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=(
                f"User email: {email}. User service role: {user_role}. "
                f"Not enough rights for the role {necessary_role}."
            ),
        )
