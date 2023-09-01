from app.managers import Managers
from models import pydantic
from models.pydantic import ObjectAlreadyExists
from services import Services


@Services.broker.listen(topic="dev.admin.cdc.project.0")
async def create_example_project(project_model: pydantic.ProjectModel) -> None:
    """
    Each new message that will be added to the topic example_topic
    will be delivered to this method and processed by it

    Args:
        project_model: data required to create a project
    """
    project_info = pydantic.PostProjectSyncRequest.model_validate(project_model)
    try:
        await Managers.projects.create_project_sync(project_info=project_info)
    except ObjectAlreadyExists:
        Managers.projects.logger.error(f"Project already exist: project_id={project_info.id}")
