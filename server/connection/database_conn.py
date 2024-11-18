import motor.motor_asyncio
from core.config import get_config

config = get_config()

# Initialize variables to store the client and db instances
_mongo_client = None
_db = None


def init_db():
    """Get the existing MongoDB client and database, or initialize them if not created."""
    global _mongo_client, _db

    if _mongo_client is None:
        # Initialize the MongoDB client only once
        _mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_url)
        _db = _mongo_client.get_database("test")

    return  _db
