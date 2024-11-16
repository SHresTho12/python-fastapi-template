from typing import Any, Optional
from functools import lru_cache
from pydantic import  validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_title: str
    project_environment_type: str
    backend_port: int = 8000
    is_reload: bool = True

    refresh_token_expire_minutes: int
    access_token_expire_minutes: int

    paseto_private_key: Any
    paseto_public_key: Any
    paseto_local_key: Any

    jwt_secret_key: str
    jwt_algorithm: str

    email_user: str
    email_user_password: str

    super_user_email: str
    super_user_password: str

    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str
    sqlalchemy_database_url: Optional[str] = None
    sqlalchemy_database_url_alembic: Optional[str] = None
    api_str: str = '/api/v1'

    frontend_base_url: str

    @validator("is_reload", pre=True)
    def parse_is_reload(cls, v: str) -> bool:
        return v.lower() in ('true', '1', 't', 'y', 'yes')

    @validator("sqlalchemy_database_url", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return (
            f"postgresql+asyncpg://{values.get('postgres_user')}:"
            f"{values.get('postgres_password')}@{values.get('postgres_server')}:"
            f"{values.get('postgres_port')}/{values.get('postgres_db')}"
        )

    @validator("sqlalchemy_database_url_alembic", pre=True)
    def assemble_db_alembic_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return (
            f"postgresql://{values.get('postgres_user')}:"
            f"{values.get('postgres_password')}@{values.get('postgres_server')}:"
            f"{values.get('postgres_port')}/{values.get('postgres_db')}"
        )

    class Config:
        case_sensitive = False
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
