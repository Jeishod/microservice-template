from fastapi import APIRouter

from app.auth import auth_manager
from app.router import (
    router_auth,
    router_projects,
    router_system,
)
from models.enum import AuthFlow


router = APIRouter()


# all routers will contain prefix="/projects/{project_uuid}" excluding router_system
router.include_router(
    router=router_projects,
    prefix="/projects/{project_id}",
    tags=["Projects"],
)

router.include_router(
    router=router_system,
    tags=["System"],
)

if auth_manager.settings.FLOW == AuthFlow.LOCAL:
    router.include_router(router=router_auth, prefix="/auth", tags=["Auth"])
