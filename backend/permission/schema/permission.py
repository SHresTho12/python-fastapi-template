from typing import List, Dict

from pydantic import BaseModel

from core.enums import Status, PermissionType
from permission.schema.group import GroupLite
from permission.schema.module import ModuleLite


class PermissionOperation(BaseModel):
    action: Dict | None = None
    permission_type: int = PermissionType.SELF_DATA.value


class PermissionBase(PermissionOperation):
    id: int


class PermissionCreate(BaseModel):
    group_id: int
    menu_permission: List[PermissionBase]

    class Config:
        from_attributes = True


class PermissionMenuView(PermissionOperation):
    id: int
    menu_name: str
    module: ModuleLite

    class Config:
        from_attributes = True


class PermissionView(BaseModel):
    module: ModuleLite
    group: GroupLite
    menu_permissions: List[PermissionMenuView] = None


class PermissionModuleView(BaseModel):
    id: int
    module_name: str
    menu_permissions: List[PermissionMenuView] = None

    class Config:
        from_attributes = True


class PermissionListView(BaseModel):
    group: GroupLite
    permissions: List[PermissionModuleView]

    class Config:
        from_attributes = True


class PermissionDetailView(BaseModel):
    detail: str


class PermissionScriptBase(PermissionBase):
    group_id: int
    module_id: int
    status: int = Status.ACTIVE.value

    class Config:
        from_attributes = True
