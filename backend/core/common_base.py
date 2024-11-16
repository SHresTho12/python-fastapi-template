from typing import Any, Optional, List, Union
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator

from core.enums import Status


def validate_string_field_check(name_field):
    if name_field is not None:
        # name_field = re.sub('[!*)@#%(&$_^]', '', name_field)
        name_field = " ".join(name_field.split())
    if not name_field:
        name_field = None
    if name_field is not None and len(name_field) < 2:
        raise ValueError(f"field length must be greater than 2")
    return name_field


def validate_none_check(name_field):
    if not name_field:
        raise ValueError("Empty value not excepted")
    return name_field


def validate_status(status_field):

    try:
        return Status(int(status_field)).name
    except Exception as e:
        print(e)
        pass
    return status_field


class CommonBase(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, name_field):
        return validate_string_field_check(name_field)

    @validator('name')
    def validate_none_name(cls, name_field):
        return validate_none_check(name_field)


class LiteResponse(BaseModel):
    id: int = None
    name: str = None

    class Config:
        from_attributes = True


class BaseResponseDataSchema(BaseModel):
    code: int
    msg: str
    data: Optional[Any]


class BaseResponse(JSONResponse):
    def __init__(
            self, code: int,
            msg: str,
            data: Union[List[dict], dict]
    ) -> None:
        data_schema = BaseResponseDataSchema(code=code, msg=msg, data=data)
        super(BaseResponse, self).__init__(
            content=jsonable_encoder(data_schema.dict()), status_code=code
        )
