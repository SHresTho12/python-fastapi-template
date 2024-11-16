from typing import List

from pydantic import BaseModel, validator

from core.common_base import (
    LiteResponse,
    validate_string_field_check,
    validate_none_check,
    validate_status
)
from core.enums import MenuType, Status


class MenuBase(BaseModel):
    name: str
    menu_type: int = MenuType.PARENT.value
    module_id: int
    api_end_point: str | None = None
    menu_serial: int | None = None
    menu_icon: str | None= None
    description: str | None= None
    menu_url: str | None= None
    parent_menu: int | None= None

    @validator('name', 'description')
    def validate_string_variable(cls, name_field):
        return validate_string_field_check(name_field)

    @validator('name')
    def validate_none_string_check(cls, name_field):
        return validate_none_check(name_field)


class MenuCreate(MenuBase):
    class Config:
        from_attributes = True


class MenuUpdate(MenuBase):
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        from_attributes = True


class ParentLite(BaseModel):
    id: int = None
    name: str = None
    menu_url: str = None

    class Config:
        from_attributes = True


class MenuView(BaseModel):
    name: str
    menu_type: int = MenuType.PARENT.value
    module_id: int
    api_end_point: str | None = None
    menu_serial: int | None= None
    menu_icon: str | None= None
    description: str | None= None
    menu_url: str | None= None
    id: int
    status: str | int
    menu_type_name: str | None= None
    module: LiteResponse | None= None
    parent: ParentLite | None= None

    # module: ModuleLite
    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)

    class Config:
        from_attributes = True


class MenuListView(BaseModel):
    items: List[MenuView | None]
    total: int
    page_limit: int
    page_number: int


class MenuDetailView(BaseModel):
    detail: str
    data: MenuView


class MenuLite(BaseModel):
    id: int
    name: str
    parent_menu: int = None

    class Config:
        from_attributes = True


class ApiEndPoint(BaseModel):
    api_end_point_name: str

    class Config:
        from_attributes = True
