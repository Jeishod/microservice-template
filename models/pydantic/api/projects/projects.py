from models.pydantic.db import ProjectModel


class PostProjectSyncRequest(ProjectModel):
    """POST request body of `/project_sync`"""


class PostProjectSyncResponse(ProjectModel):
    """POST response body of `/project_sync`"""


class PostProjectAsyncRequest(ProjectModel):
    """POST request body of `/project_async`"""


class PostProjectAsyncResponse(ProjectModel):
    """POST response body of `/project_async`"""


class GetProjectResponse(ProjectModel):
    """GET response body of `/project"""
