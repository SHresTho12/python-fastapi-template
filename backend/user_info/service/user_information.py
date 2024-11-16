from typing import Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from auth import User
from config import logger, get_settings
from core.const import FREE_CREDIT_BALANCE
from core.enums import  Status
from core.utils import upload_file_to_s3
from user_info import UserInformationRepo


class UserInformationService:
    def __init__(self):
        self.repository = UserInformationRepo()

    async def signup_time_create_user(self, users: User):
        user_info_data = {
            "user_id": users.id
        }
        async with self.repository:
            response = await self.repository.create(user_info_data)

        return response.__dict__

    async def get_user_info(self, user_id):
        user_info = None
        async with self.repository:
            user_info = await self.repository.get(
                filters=(
                    self.repository._model.user_id == user_id,
                )
            )
        return user_info

    async def update_user_info(
            self,
            user_id: int,
            user_info_data: dict
    ):
        user_info_obj = await self.get_user_info(user_id)
        async with self.repository:
            await self.repository.update(
                user_info_obj,
                user_info_data
            )
        return True

    async def profile_picture_upload(self, current_user: "User", file: "File"):
        user_info_data = await self.get_user_info(current_user.id)
        if user_info_data:
            try:
                content_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'

                file = await upload_file_to_s3(
                    file,
                    f"{current_user.username}.{content_type}",
                    project_environment=get_settings().project_environment_type,
                    module_name="profile_picture",
                    file_type="images",

                )
                return file
            except Exception as e:
                logger.error(f"Failed to upload asset. Reason: {e}")
        return {"detail": "Failed"}
