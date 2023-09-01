import uuid

from app.cache import Cache
from app.db import Database
from app.managers.managers_base import ManagersBase
from models import pydantic
from services import Services


class ProjectsManager(ManagersBase):
    """Working with projects"""

    async def create_project_sync(
        self, project_info: pydantic.PostProjectSyncRequest
    ) -> pydantic.PostProjectSyncResponse:
        """Logic of endpoint POST `/{project}/project_sync`

        Args:
            project_info (pydantic.PostProjectSyncRequest): info about the project to create

        Returns:
            pydantic.PostProjectSyncResponse: created project
        """
        project_model = pydantic.ProjectModel.model_validate(project_info)
        project = await Database.projects.create(project_model=project_model)
        await Cache.projects.create(project=project)
        return pydantic.PostProjectSyncResponse.model_validate(project)

    async def create_project_async(
        self, project_info: pydantic.PostProjectAsyncRequest
    ) -> pydantic.PostProjectAsyncResponse:
        """Logic of endpoint POST `/{project}/project_async`

        Args:
            project_info (pydantic.PostProjectAsyncRequest): info about the project to create

        Returns:
            pydantic.PostProjectAsyncResponse: created project
        """
        project_model = pydantic.ProjectModel.model_validate(project_info)
        await Services.broker.produce(topic="dev.admin.cdc.project.0", message=project_model)
        return pydantic.PostProjectAsyncResponse.model_validate(project_info)

    async def get_project(self, project_id: uuid.UUID) -> pydantic.GetProjectResponse:
        """Logic of endpoint GET `/{project}/project`

        Args:
            project_id (uuid.UUID): project ID

        Raises:
            pydantic.ObjectNotFound: if project was not found

        Returns:
            pydantic.GetProjectResponse: project
        """
        project_cache = await Cache.projects.get(project_id=project_id)
        if project_cache:
            return pydantic.GetProjectResponse(
                id=project_cache.id, name=project_cache.name, description=project_cache.description
            )
        project = await Database.projects.get(project_id=project_id)
        if not project:
            raise pydantic.ObjectNotFound(message_prefix="Object not found", project_id=project_id)
        await Cache.projects.create(project=project)
        return pydantic.GetProjectResponse.model_validate(project)
