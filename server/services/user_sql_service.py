from typing import Optional, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from repositories.user_sql_repo import UserRepo
from models.user_sql_model import User


class UserService:


    def __init__(self , sql_db: Session):

        self.user_repo = UserRepo(sql_db)
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:

        return self.password_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:

        return self.password_context.verify(plain_password, hashed_password)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        is_superuser: bool = False
    ) -> User:

        hashed_password = self.hash_password(password)
        return self.user_repo.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_superuser=is_superuser,
        )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:

        user = self.user_repo.get_user_by_username(username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:

        return self.user_repo.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:

        return self.user_repo.get_user_by_email(email)

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:

        return self.user_repo.get_all_users(limit=limit, offset=offset)

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:

        if "password" in kwargs:
            kwargs["hashed_password"] = self.hash_password(kwargs.pop("password"))
        return self.user_repo.update_user(user_id, **kwargs)

    def delete_user(self, user_id: int) -> bool:

        return self.user_repo.delete_user(user_id)
