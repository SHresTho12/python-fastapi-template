from typing import List

from pydantic import BaseModel, validator

from core.common_base import CommonBase, validate_status
from core.enums import Status


class GroupUpdate(CommonBase):
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        from_attributes = True


class GroupCreate(CommonBase):
    class Config:
        from_attributes = True


class GroupView(CommonBase):
    id: int
    status: str | int | None = None

    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)

    class Config:
        from_attributes = True


class GroupListView(BaseModel):
    items: List[GroupView | None]
    total: int
    page_limit: int
    page_number: int


class GroupDetailView(BaseModel):
    detail: str
    data: GroupView


class GroupLite(CommonBase):
    id: int

    class Config:
        from_attributes = True
