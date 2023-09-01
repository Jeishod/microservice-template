from fastapi import (
    APIRouter,
    status,
)
from fastapi.responses import JSONResponse

router_system = APIRouter()


@router_system.get(path="/")
async def healthcheck() -> JSONResponse:
    """Service status"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ok",
        },
    )
