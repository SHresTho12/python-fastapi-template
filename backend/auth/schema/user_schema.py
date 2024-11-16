from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, validator, Json
from fastapi import HTTPException, status


class UserCommonBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str


class UserBase(UserCommonBase):
    email: EmailStr
    # version: str = None


class UserResponse(UserBase):
    id: int
    created_at: datetime | None

    class Config:
        from_attributes = True


class UserActionResponse(BaseModel):
    detail: str
    data: UserResponse


class UserSignUPBase(UserCommonBase):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password must be at least 8 characters long."
            )
        return password


class UserLogin(BaseModel):
    email: str
    password: str


class SignupResponse(UserBase):
    access_token: str
    refresh_token: str
    token_type: str
    expiry_time: str = None


class LoginResponse(BaseModel):
    email: str
    access_token: str
    refresh_token: str
    token_type: str
    expiry_time: str = None

class RefreshTokenResponse(LoginResponse):
    pass

class RefreshToken(BaseModel):
    refresh_token: str


class PasswordBase(BaseModel):
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_password(cls, new_password):
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password must be at least 8 characters long."
            )
        return new_password

    class Config:
        from_attributes = True


class PasswordChange(PasswordBase):
    old_password: str

    class Config:
        from_attributes = True


class ResetPassword(PasswordBase):
    class Config:
        from_attributes = True


class ForgetPassword(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True


class UserLite(BaseModel):
    id: int
    email: str = None
    full_name: str = None

    class Config:
        from_attributes = True
