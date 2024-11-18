from datetime import datetime

import logging
from connection.database_conn import init_db

logger = logging.getLogger(__name__)

class StatisticsRepo:
    def __init__(self):
        self.db = init_db()
        self.statistics_collection = self.get_statistics_collection()
        self.initialize_statistics()

    def get_statistics_collection(self):
        return self.db.get_collection("statistics")

    def initialize_statistics(self):
        """
        Initialize the statistics collection with default values if it is empty.
        """
        if self.statistics_collection.count_documents({}) == 0:
            logger.info("Initializing statistics collection with default values")
            default_statistics = {
                "request_count": 0,
                "total_file_size": 0,
                "database_last_updated": datetime.now().strftime("%I:%M:%S %p"),
                "total_customer_agents": 0,
            }
            self.statistics_collection.insert_one(default_statistics)

    async def get_one(self):
        return await self.statistics_collection.find_one({})

    async def add(self, statistics_data: dict):
        result = await self.statistics_collection.insert_one(statistics_data)
        return str(result.inserted_id)

    async def update(self, query, update_data: dict, upsert: bool = True):
        """Update the statistics document with the given data."""
        # Check if the update_data contains a $ operator (like $inc, $set)
        if any(key.startswith("$") for key in update_data):
            # If it contains $ operators, use the update_data as-is
            await self.statistics_collection.update_one(
                query,
                update_data,
                upsert=upsert
            )
        else:
            # Otherwise, use $set by default
            await self.statistics_collection.update_one(
                query,
                {"$set": update_data},
                upsert=upsert
            )