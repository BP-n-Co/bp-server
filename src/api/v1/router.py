from fastapi import APIRouter

from .repositories import repositories_routeur

router = APIRouter(prefix="/v1")

router.include_router(repositories_routeur)
