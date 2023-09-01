import uuid

from app.cache import CacheBase
from models import (
    pydantic,
    redisorm,
)


class ProjectCache(CacheBase):
    """Working with projects"""

    async def get(self, project_id: uuid.UUID) -> redisorm.Projects | None:
        """Get project cache by its ID.

        Args:
            project_id (uuid.UUID): project ID

        Returns:
            redisorm.Projects | None: project cache if found, None otherwise
        """
        return await redisorm.Projects.get(id=project_id)

    async def create(self, project: pydantic.ProjectModel) -> redisorm.Projects:
        """Cache project.

        Args:
            project (pydantic.ProjectModel): project model

        Returns:
            redisorm.Projects: project cache
        """
        project_cache = redisorm.Projects(**project.model_dump())
        await project_cache.save()
        return project_cache
