from app.cache import CacheBase
from app.cache.project import ProjectCache


class Cache(CacheBase):
    """Application cache manager"""

    projects: ProjectCache = ProjectCache()
