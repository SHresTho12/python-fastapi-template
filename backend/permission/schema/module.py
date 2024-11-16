from typing import List

from pydantic import BaseModel, validator

from core.common_base import (
    CommonBase,
    validate_status
)
from core.enums import Status


class ModuleUpdate(CommonBase):
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        from_attributes = True


class ModuleCreate(CommonBase):
    class Config:
        from_attributes = True


class ModuleView(CommonBase):
    id: int
    status: str | int

    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)

    class Config:
        from_attributes = True


class ModuleDetailView(BaseModel):
    detail: str
    data: ModuleView

    class Config:
        from_attributes = True


class ModuleListView(BaseModel):
    items: List[ModuleView | None]
    total: int
    page_limit: int
    page_number: int


class ModuleLite(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
