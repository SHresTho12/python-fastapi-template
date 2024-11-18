
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base2

from core.config import get_config

config = get_config()

# Initialize variables to store the engine and session instances
_engine = None
_session = None
Base = declarative_base2()

def init_sql_db():
    """Get the existing SQL Alchemy engine and session, or initialize them if not created."""
    global _engine, _session

    if _engine is None:
        # Initialize the SQL Alchemy engine only once
        _engine = create_engine(config.postgres_url)
        _session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    return _session