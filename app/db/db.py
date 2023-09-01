from app.db.db_base import DatabaseBase
from app.db.project import ProjectDb
from app.db.project_user import ProjectUserDb
from app.db.service_user import ServiceUserDb
from app.db.user import UserDb


class Database(DatabaseBase):
    """Application CRUD"""

    projects: ProjectDb = ProjectDb()
    users: UserDb = UserDb()
    project_users: ProjectUserDb = ProjectUserDb()
    service_users: ServiceUserDb = ServiceUserDb()
