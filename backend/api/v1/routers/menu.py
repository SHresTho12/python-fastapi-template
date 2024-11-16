
from permission.schema.menu import MenuCreate, MenuUpdate, MenuView, MenuDetailView
from permission.service.menu import MenuService


# from app.api.dependencies.check_permissions import CheckPermission

#
# # city_check_permission = lambda permission: CheckPermission("city", permission)

from fastapi import APIRouter, Depends, status, Query, Request
from fastapi_pagination import LimitOffsetPage, paginate

from core.const import FILTERTYPE
from core.utils import request_user

menu_router = r = APIRouter()


@r.post(
    "",
    response_model=MenuDetailView,
    status_code=status.HTTP_201_CREATED
)
async def create(
        request: Request,
        menu: MenuCreate,
        current_user=Depends(request_user),
        service: MenuService = Depends(MenuService)
):
    created_menu = await service.create_menu(request, current_user, menu)
    return MenuDetailView(detail="Menu created successfully!", data=created_menu)


@r.get("", response_model=LimitOffsetPage[MenuView])
async def list(
        request: Request,
        current_user=Depends(request_user),
        name: str | None = Query(default=None, alias=f"filter[type][{FILTERTYPE.EXACT}]"),
        service: MenuService = Depends(MenuService)
):
    menus = await service.all(query=request.query_params)
    return paginate(menus)


@r.get("/{menu_id}", response_model=MenuView)
async def get(
        menu_id: int,
        current_user=Depends(request_user),
        service: MenuService = Depends(MenuService)
):
    menus = await service.get(menu_id)
    return menus


@r.put("/{menu_id}", response_model=MenuDetailView)
async def update(
        menu_id: int,
        request: Request,
        menu: MenuUpdate,
        current_user=Depends(request_user),
        service: MenuService = Depends(MenuService)
):
    updated_menu = await service.update_menu(
        id=menu_id,
        request=request,
        updated_data=menu,
        current_user=current_user
    )
    return MenuDetailView(detail="Menu update successfully!", data=updated_menu)


@r.delete("/{menu_id}", response_model=str)
async def delete(
        menu_id: int,
        current_user=Depends(request_user),
        service: MenuService = Depends(MenuService)
):
    await service.delete_menu(menu_id, current_user)
    return "Menu deleted successfully!"


