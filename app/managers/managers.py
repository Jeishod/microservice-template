from app.managers.auth import AuthManager
from app.managers.managers_base import ManagersBase
from app.managers.projects import ProjectsManager


class Managers(ManagersBase):
    """Application managers"""

    auth: AuthManager = AuthManager()
    projects: ProjectsManager = ProjectsManager()
