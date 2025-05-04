from fastapi import APIRouter

from .repository import repository_routeur

router = APIRouter(prefix="/v1")

router.include_router(repository_routeur)
