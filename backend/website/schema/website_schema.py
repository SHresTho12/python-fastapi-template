from pydantic import BaseModel, validator

class WebsiteCreateSchema(BaseModel):
    name: str

class WebsiteReadSchema(BaseModel):
    id: int
    name: str

class WebsiteViewResponse(BaseModel):
    detail: str
    data: WebsiteReadSchema

    class Config:
        from_attributes = True

class WebsiteUpdateSchema(WebsiteCreateSchema):
    status: int