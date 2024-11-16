from fastapi import APIRouter

from api.v1 import routers
from core.const import MAP_URL

api_router = APIRouter()


api_router.include_router(
    routers.auth_router,
    prefix=MAP_URL("auth"),
    tags=["auth"]
)

api_router.include_router(
    routers.group_router,
    prefix=MAP_URL("groups"),
    tags=["Group"]
)
api_router.include_router(
    routers.module_router,
    prefix=MAP_URL("module"),
    tags=["Module"]
)
api_router.include_router(
    routers.menu_router,
    prefix=MAP_URL("menu"),
    tags=["Menu"]
)
api_router.include_router(
    routers.user_info_router,
    prefix=MAP_URL("user"),
    tags=["Personal Info"]
)

api_router.include_router(
    routers.permission_router,
    prefix=MAP_URL("permission"),
    tags=["Permission"]
)

api_router.include_router(
    routers.public_router,
    prefix=MAP_URL("public"),
    tags=["public"]
)

api_router.include_router(
    routers.user_router,
    prefix=MAP_URL("users"),
    tags=["Users"]
)

api_router.include_router(
    routers.website_router,
    prefix=MAP_URL("websites"),
    tags=["websites"]
)
