from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.stores import router as stores_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(stores_router)
