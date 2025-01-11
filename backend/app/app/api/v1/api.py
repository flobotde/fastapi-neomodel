from fastapi import APIRouter
from app.api.v1.endpoints import (
    user,
    login,
    role,
    group,
    cache,
    weather,
    report,
)

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(group.router, prefix="/group", tags=["group"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
)
