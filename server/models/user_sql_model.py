
from sqlalchemy import Column, Integer, String , Boolean
from connection.sql_database_conn import Base
from pydantic import BaseModel, EmailStr

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    



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
