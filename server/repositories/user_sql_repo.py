from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy import update, delete
from models.user_sql_model import User

from connection.sql_database_conn import get_db




class UserRepo:
    """Repository for interacting with the User SQL database."""

    def __init__(self, sql_db: Session):
        """
        Initialize the UserRepo class with a database session.
        
        Args:
            sql_db (Session): SQLAlchemy session instance.
        """
        self.sql_db = sql_db

    def get_user_by_id(self, user_id: int) -> User | None:

        try:
            result = self.sql_db.query(User).filter(User.id == user_id).one()
            return result
        except NoResultFound:
            return None

    def get_user_by_username(self, username: str) -> User | None:

        
        result = self.sql_db.query(User).filter(User.username == username).one_or_none()
        return result

    def get_user_by_email(self, email: str) -> User | None:

        query = select(User).where(User.email == email)
        result = self.sql_db.execute(query).one_or_none()
        return result

    def create_user(self, username: str, email: str, hashed_password: str, is_superuser: bool = False) -> User:
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_superuser=is_superuser
        )
        try:
            self.sql_db.add(new_user)
            self.sql_db.commit()
            self.sql_db.refresh(new_user)
            return new_user
        except IntegrityError:
            self.sql_db.rollback()
            raise ValueError("A user with this username or email already exists.")

    def update_user(self, user_id: int, **kwargs) -> User | None:

        try:
            query = update(User).where(User.id == user_id).values(**kwargs).execution_options(synchronize_session="fetch")
            self.sql_db.execute(query)
            self.sql_db.commit()
            return self.get_user_by_id(user_id)
        except IntegrityError:
            self.sql_db.rollback()
            raise ValueError("Failed to update user due to a conflict with existing data.")

    def delete_user(self, user_id: int) -> bool:

        query = delete(User).where(User.id == user_id)
        result = self.sql_db.execute(query)
        self.sql_db.commit()
        return result.rowcount > 0

    def get_all_users(self, limit: int = 100, offset: int = 0) -> list[User]:

        query = select(User).limit(limit).offset(offset)
        result = self.sql_db.execute(query).scalars().all()
        return result
