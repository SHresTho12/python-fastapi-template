from fastapi import status, Depends, HTTPException

from auth import User
from core.const import GROUP_LIST_REVERSE
from core.enums import PermissionType
from core.utils import request_user
from permission.repository.menu import MenuRepo
from permission.repository.permission import PermissionRepo


class CheckPermission:
    def __init__(self, api_end_point: str, permission: str):
        self.api_end_point = api_end_point
        self.menu_repo = MenuRepo()
        self.permission_repo = PermissionRepo()
        self.permission = permission

    async def __call__(self, user: User = Depends(request_user)):
        if any(group.id == GROUP_LIST_REVERSE["Super Admin"] for group in user.groups):
            return PermissionType.ALL_DATA.value

        # Fetch menu data
        menu_data = await self._fetch_menu_data()
        if not menu_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

        # Fetch user permissions
        permission_type = await self._fetch_user_permissions(user.groups, menu_data.id)
        if permission_type:
            return permission_type
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    async def _fetch_menu_data(self):
        async with self.menu_repo as repo:
            return await repo.get(
                filters=(
                    repo._model.api_end_point == self.api_end_point,
                    repo._model.deleted_at.is_(None)
                )
            )

    async def _fetch_user_permissions(self, groups, menu_id):
        group_ids = [group.id for group in groups]
        async with self.permission_repo as repo:
            permissions = await repo.list(
                filters=(
                    repo._model.group_id.in_(group_ids),
                    repo._model.menu_id == menu_id,
                    repo._model.deleted_at.is_(None)
                )
            )

        for permission in permissions:
            if permission.action.get(self.permission):
                return permission.permission_type
        return None
