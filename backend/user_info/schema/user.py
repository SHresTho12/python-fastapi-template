from pydantic import BaseModel, validator
from typing import List
from core.common_base import LiteResponse
from core.enums import Gender
from core.model_base import CommonBase


class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str

class UserCreate(UserBase):
    password: str
    group_id: int
    pass

class UserEdit(UserBase):
    group_id: int
    pass

class UserView(UserBase):
    id: int
    groups: List[LiteResponse] | None = None

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserViewResponse(BaseModel):
    detail: str
    data: UserResponse

    class Config:
        from_attributes = True