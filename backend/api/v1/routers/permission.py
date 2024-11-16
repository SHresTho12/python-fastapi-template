from typing import Optional, Any

from fastapi import APIRouter, Depends, status, Request, HTTPException


from core.common_base import BaseResponse, BaseResponseDataSchema
from core.const import GROUP_LIST_REVERSE
from core.utils import request_user
from permission.schema.permission import PermissionCreate
from permission.service.permission import PermissionService



# from app.api.dependencies.check_permissions import CheckPermission


# city_check_permission = lambda permission: CheckPermission("city", permission)


class PermissionRouter:
    def __init__(self):
        self.router = APIRouter()
        self.permission_service = PermissionService()

        self.router.get(
            "",
            status_code=status.HTTP_200_OK,
        )(self.get_permission)

        self.router.post(
            "",
            response_model=str,
            status_code=status.HTTP_201_CREATED,
        )(self.permission_set)

    async def permission_set(
            self,
            request: Request,
            permission_data: PermissionCreate,
            current_user=Depends(request_user)
    ):
        """
        Set a  Permission
        """
        if permission_data.group_id == GROUP_LIST_REVERSE['Super Admin']:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Super user get all menu permission. So, can't set menu permission for this user"
            )
        await self.permission_service.set_group_based_permission(request, permission_data)
        return "Successfully set Permissions"


    async def get_permission(
            self,
            request: Request,
            group_id: int,
            module_id: Optional[int] = 0,
            current_user=Depends(request_user),
    ):
        return BaseResponse(
            code=status.HTTP_200_OK,
            msg="Fetched successfully.",
            data=await self.permission_service.get_group_based_permission(
                request, group_id, module_id
            )
        )

    
permission_router = PermissionRouter().router
