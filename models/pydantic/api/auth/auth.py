from pydantic import BaseModel

from models.pydantic.db import (
    UserModel,
    UserWithPassword,
)


class PostRegisterRequest(UserWithPassword):
    """POST request body of `/register`"""


class PostRegisterResponse(UserModel):
    """POST response body of `/register`"""


class PostLoginResponse(BaseModel):
    """POST response body of `/login`"""

    access_token: str
