from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from core.schemas.user import UserCreate, UserResponse, UserUpdate
from services.user_sql_service import UserService
from connection.sql_database_conn import Base , get_db , engine
from models import user_sql_model
user_router = APIRouter()


user_sql_model.Base.metadata.create_all(bind=engine)

@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    existing_user = user_service.get_user_by_email(user.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    created_user = user_service.create_user(
        username=user.username,
        email=user.email,
        password=user.password,
        is_superuser=user.is_superuser,
    )
    return created_user


@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return user


@user_router.get("/", response_model=List[UserResponse])
def list_users(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_all_users(limit=limit, offset=offset)


@user_router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    updated_user = user_service.update_user(user_id, **user.dict(exclude_unset=True))

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return updated_user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserService(db)
    is_deleted = user_service.delete_user(user_id)

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    return None
