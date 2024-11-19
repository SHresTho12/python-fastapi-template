from pydantic import BaseModel, EmailStr

# Schema for creating a new user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superuser: bool = False


# Schema for updating an existing user
class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None
    is_active: bool = None
    is_superuser: bool = None


# Schema for user response
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True
