from typing import Any

from fastapi import HTTPException, status

from auth.model import User
from auth.repository.auth_repository import AuthRepo


class UserService:
    def __init__(self):
        self.repository = AuthRepo()
        self._model = User

    async def fetch(self, filters):
        async with self.repository:
            user = await self.repository.get(filters)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        return user