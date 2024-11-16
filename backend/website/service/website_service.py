from typing import Type
from fastapi import Depends, status, HTTPException


from auth import User
from core.service.base_service import BaseService
from core.utils import request_user
from website.repository.website_repository import WebsiteRepository
from website.schema.website_schema import WebsiteReadSchema, WebsiteCreateSchema


class WebsiteService(BaseService):
    def __init__(
            self,
            repository: WebsiteRepository = Depends(WebsiteRepository),
            read_schema: Type[WebsiteReadSchema] = WebsiteReadSchema,
            current_user: User = Depends(request_user)
    ):
        super().__init__(repository=repository, read_schema=read_schema)
        self.current_user = current_user

    async def _validate(self, data: WebsiteCreateSchema , record_id: int | None = None):
        if record_id:
            website_info = await self.get_db_obj(record_id)
            print("current user ",self.current_user.id)
            if self.current_user.id  in [website_info.user_id, website_info.created_by_id]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Not Found"
                )