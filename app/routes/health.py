from fastapi import APIRouter

from app.models.api import OKResponse

router = APIRouter()


@router.get("/health")
async def status() -> OKResponse:
    return OKResponse()
