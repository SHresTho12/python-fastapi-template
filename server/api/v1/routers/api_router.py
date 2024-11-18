
from fastapi import APIRouter

from api.v1.routers.auth_router import auth_router
from api.v1.routers.statistics import stats_router
from api.v1.routers.user_router import user_router
from jobs.file_update_job import cronjob
api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])

# api_router.include_router(cronjob)
api_router.include_router(stats_router, prefix="/stats", tags=["stats"])