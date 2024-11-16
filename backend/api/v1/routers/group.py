from fastapi import APIRouter, Depends, status, Query, Request
from fastapi_pagination import LimitOffsetPage, paginate

from api.dependencies.check_permissions import CheckPermission
from core.utils import request_user
from permission.schema.group import GroupCreate, GroupUpdate, GroupView, GroupDetailView
from permission.service.group import GroupService

check_permission = lambda permission: CheckPermission("groups", permission)

group_router = r = APIRouter()


@r.post(
    "",
    response_model=GroupDetailView,
    status_code=status.HTTP_201_CREATED,
)
async def create(
        groupe: GroupCreate,
        current_user=Depends(request_user),
        service: GroupService = Depends(GroupService),
        permission_check=Depends(check_permission('create'))
):
    created_group = await service.insert(groupe, current_user)
    return GroupDetailView(detail="Group created successfully!", data=created_group)


@r.get("", response_model=LimitOffsetPage[GroupView])
async def list(
        request: Request,
        current_user=Depends(request_user),
        service: GroupService = Depends(GroupService),
        permission_check=Depends(check_permission('list'))
):
    groups = await service.all(query=request.query_params)
    return paginate(groups)


@r.get("/{group_id}", response_model=GroupView)
async def get(
        group_id: int,
        current_user=Depends(request_user),
        service: GroupService = Depends(GroupService),
        permission_check=Depends(check_permission('view'))
):
    groups = await service.get(group_id)
    return groups


@r.put("/{group_id}", response_model=GroupDetailView)
async def update(
        group_id: int,
        group: GroupUpdate,
        current_user=Depends(request_user),
        service: GroupService = Depends(GroupService),
        permission_check=Depends(check_permission('edit'))
):
    updated_group = await service.edit(group_id, group, current_user)
    return GroupDetailView(detail="Group update successfully!", data=updated_group)


@r.delete("/{group_id}", response_model=str)
async def delete(
        group_id: int,
        current_user=Depends(request_user),
        service: GroupService = Depends(GroupService),
        permission_check=Depends(check_permission('delete'))
):
    deleted_group = await service.delete(group_id, current_user)
    return "Group deleted successfully!"
