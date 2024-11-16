from fastapi import APIRouter, Depends, status, Form, UploadFile, File, Query, Request
from fastapi_pagination import LimitOffsetPage, paginate

from core.const import FILTERTYPE
from core.utils import request_user
from user_info.schema.user import UserView, UserCreate, UserEdit, UserViewResponse
from user_info.service.user import UserService

user_router = r = APIRouter()


@r.post(
    "",
    response_model=UserViewResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
        user: UserCreate,
        current_user=Depends(request_user),
        service: UserService = Depends(UserService)
):

    created_user = await service.insert(user, current_user)
    return UserViewResponse(detail="User created successfully!", data = created_user)


@r.get("", response_model=LimitOffsetPage[UserView])
async def list(
        request: Request,
        name: str | None = Query(default=None, alias=f"filter[type][{FILTERTYPE.EXACT}]"),
        current_user=Depends(request_user),
        service: UserService= Depends(UserService)):
    users = await service.all(query=request.query_params)
    return paginate(users)


@r.get("/{user_id}", response_model=UserView)
async def get(
        user_id: int,
        service: UserService = Depends(UserService)
):
    users = await service.get(user_id)
    return users


@r.put("/{user_id}", response_model=UserViewResponse)
async def update(
        user_id: int,
        user: UserEdit,
        current_user=Depends(request_user),
        service: UserService= Depends(UserService)
):
    updated_user = await service.edit(user_id, user, current_user)
    return UserViewResponse(detail="User update successfully!", data=updated_user)


@r.delete("/{user_id}", response_model=str)
async def delete(
        user_id: int,
        current_user=Depends(request_user),
        service: UserService= Depends(UserService)
):
    deleted_user = await service.delete(user_id, current_user)
    return  "User deleted successfully!"




