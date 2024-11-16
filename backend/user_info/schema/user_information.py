from datetime import date
from pydantic import BaseModel, validator

from core.enums import Gender


class UserInfoView(BaseModel):
    address: str = None
    company_website: str = None
    client_type: int = None
    client_type_name: str = None
    credit_balance: float = None
    subscription_date: date = None
    subscription_expired_date: date = None


class PersonalUserInfoView(BaseModel):
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    company_website: str | None = None
    contact_information: str | None = None
    personal_information: str | None = None
    date_of_birth: str | None = None
    profile_picture: str | None = None
    gender: str | None = None

    @validator('gender')
    def validate_status_response(cls, gender_id):
        try:
            return Gender(int(gender_id)).name.title()
        except:
            pass
        return gender_id

    @validator('profile_picture')
    def validate_icon(cls, value):
        if value and 's3' not in value:
            return get_signed_uri(value)
        else:
            return value



    class Config:
        from_attributes = True


class PersonalUserInfoEdit(BaseModel):
    first_name: str = None
    last_name: str = None
    phone: str = None
    address: str = None
    company_website: str = None
    contact_information: str = None
    personal_information: str = None
    date_of_birth: date = None
    gender: int = None

    @validator('gender')
    def validate_status(cls, gender_field):
        values = [data.value for data in Gender]
        if gender_field not in values:
            raise ValueError("Invalid gender!")
        return gender_field