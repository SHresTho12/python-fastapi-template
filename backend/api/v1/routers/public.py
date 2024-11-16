
from fastapi import APIRouter, Request

from core.utils import get_all_status

public_router = r = APIRouter()


class PublicRouter:
    def __init__(self):
        self.router = APIRouter()

        self.router.get(
            "/all_keys",
        )(self.get_all_keys)

    async def get_all_keys(self, request: Request):
        return await get_all_status(request)


public_router = PublicRouter().router
