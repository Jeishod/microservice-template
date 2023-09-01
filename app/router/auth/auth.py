from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    status,
)

from app import dependencies
from app.managers import Managers
from models import pydantic
from models.enum import ServiceRole


router_auth = APIRouter()


@router_auth.post(
    path="/register",
    response_model=pydantic.PostRegisterResponse,
    summary="Register new user. Only for local development.",
    status_code=status.HTTP_201_CREATED,
)
async def register(user_info: pydantic.PostRegisterRequest) -> pydantic.PostRegisterResponse:
    """
    Register a new user. Only for local development.

    ### Request
    #### Body
    * **id**: user ID. None if ID has to be autogenerated.
    * **email**: user email
    * **name**: user name
    * **password**: user password

    ### Response body
    * **id**: user ID
    * **email**: user email
    * **name**: user name
    * **password**: user password
    """
    return await Managers.auth.register(user_info=user_info)


@router_auth.post(
    path="/jwt/login",
    response_model=pydantic.PostLoginResponse,
    summary="Login by email and password. Only for local development.",
    status_code=status.HTTP_200_OK,
)
async def login(
    username: Annotated[str, Form(description="User email")],
    password: Annotated[str, Form(description="User password")],
) -> pydantic.PostLoginResponse:
    """
    Login by user credentials.

    ### Request
    #### Form
    * **username**: user email (query)
    * **password**: user password (query)

    ### Response body
    * **access_token**: JWT access token
    """
    return await Managers.auth.login(username=username, password=password)