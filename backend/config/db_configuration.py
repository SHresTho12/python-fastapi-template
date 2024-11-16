import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.log_configuration import logger
from config.settings_configuration import get_settings

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


engine = create_async_engine(
    get_settings().sqlalchemy_database_url,
    pool_pre_ping=True,
    pool_recycle=60,
    pool_size=100,
    max_overflow=0,
)
# Dependency

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = None
    try:
        session = async_session()
        async with session.begin():
            yield session
    except Exception as e:
        logger.error(str(e))
        raise
    finally:
        if session is not None:
            await session.close()