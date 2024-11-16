from fastapi import APIRouter, Depends, status, Query, Request
from fastapi_pagination import LimitOffsetPage, paginate

from core.const import FILTERTYPE
from core.utils import request_user
from permission.schema.module import ModuleCreate, ModuleUpdate, ModuleView, ModuleDetailView
from permission.service.module import ModuleService

module_router = r = APIRouter()


@r.post(
    "",
    response_model=ModuleDetailView,
    status_code=status.HTTP_201_CREATED
)
async def create(
        module: ModuleCreate,
        current_user=Depends(request_user),
        service: ModuleService = Depends(ModuleService)
):
    created_modul = await service.insert(module, current_user)
    return ModuleDetailView(detail="Module created successfully!", data=created_modul)


@r.get("", response_model=LimitOffsetPage[ModuleView])
async def list(
        request: Request,
        current_user=Depends(request_user),
        name: str | None = Query(default=None, alias=f"filter[type][{FILTERTYPE.EXACT}]"),
        service: ModuleService = Depends(ModuleService)):
    moduls = await service.all(query=request.query_params)
    return paginate(moduls)


@r.get("/{module_id}", response_model=ModuleView)
async def get(
        module_id: int,
        current_user=Depends(request_user),
        service: ModuleService = Depends(ModuleService)
):
    moduls = await service.get(module_id)
    return moduls


@r.put("/{module_id}", response_model=ModuleDetailView)
async def update(
        module_id: int,
        module: ModuleUpdate,
        current_user=Depends(request_user),
        service: ModuleService = Depends(ModuleService)
):
    updated_modul = await service.edit(module_id, module, current_user)
    return ModuleDetailView(detail="Module update successfully!", data=updated_modul)


@r.delete("/{module_id}", response_model=str)
async def delete(
        module_id: int,
        current_user=Depends(request_user),
        service: ModuleService = Depends(ModuleService)
):
    deleted_modul = await service.delete(module_id, current_user)
    return "Module deleted successfully!"
