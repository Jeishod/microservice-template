import uuid

from fastapi import (
    APIRouter,
    status,
)

from app.managers import Managers
from models import pydantic


router_projects = APIRouter()


@router_projects.post(
    path="/project_sync",
    response_model=pydantic.PostProjectSyncResponse,
    summary="Synchronous project creation",
    status_code=status.HTTP_201_CREATED,
)
async def create_project_sync(project_info: pydantic.PostProjectSyncRequest) -> pydantic.PostProjectSyncResponse:
    """
    Create project in a sync way.

    ### Request
    #### Body
    * **id**: project ID. None if ID has to be autogenerated.
    * **name**: project name
    * **description**: project description. Can be None.

    ### Response body
    * **id**: project ID
    * **name**: project name
    * **description**: project description. Can be None.
    """
    return await Managers.projects.create_project_sync(project_info=project_info)


@router_projects.post(
    path="/project_async",
    response_model=pydantic.PostProjectAsyncResponse,
    summary="Asynchronous project creation",
    status_code=status.HTTP_201_CREATED,
)
async def create_project_async(project_info: pydantic.PostProjectAsyncRequest) -> pydantic.PostProjectAsyncResponse:
    """
    Create project in async way (via message broker).

    ### Request
    #### Body
    * **id**: project ID. None if ID has to be autogenerated.
    * **name**: project name
    * **description**: project description. Can be None.

    ### Response
    * **id**: project ID
    * **name**: project name
    * **description**: project description. Can be None.
    """
    return await Managers.projects.create_project_async(project_info=project_info)


@router_projects.get(
    path="/project",
    response_model=pydantic.GetProjectResponse,
    summary="Find created project",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": pydantic.ProjectNotFoundModel},
    },
)
async def get_project(project_id: uuid.UUID) -> pydantic.GetProjectResponse:
    """
    Get project by its ID.

    ### Request
    #### Query parameters
    * **project_id**: project ID

    ### Response
    * **id**: project ID
    * **name**: project name
    * **description**: project description. Can be None.
    """
    return await Managers.projects.get_project(project_id)