from pydantic import BaseModel
class ValidationResponse(BaseModel):
    title: str
    field: str
    location: str
    message: str


class AppValidationResponse(BaseModel):
    errors: list[ValidationResponse]