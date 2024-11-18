from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from constants.auth_consts import SUPER_ADMIN_ROLE


class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    email: str
    access_token: str
    refresh_token: str
    token_type: str

class SuperAdmin(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = SUPER_ADMIN_ROLE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RefreshTokenReq(BaseModel):
    refresh_token: str

class AddNewMemberPayload(BaseModel):
    email: str
    full_name: str
    password : str
    role: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None