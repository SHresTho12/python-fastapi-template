from connection.database_conn import init_db


class HistoryRepo:
    def __init__(self):
        """Initialize MongoDB connection and collection using init_db."""
        self.db = init_db()
        self.history_collection = self.get_history_collection()

    def get_history_collection(self):
        """Return the history collection."""
        return self.db.get_collection("chat_sessions")

    async def get_one(self, query=None, projection=None, sort_field: str = None, sort_order: int = -1):
        """Fetch a single history document based on conversation_id and user_id."""
        if query is None:
            query = {}

        cursor = self.history_collection.find(query, projection)
        if sort_field:
            cursor = cursor.sort(sort_field, sort_order)
        
        return await cursor.limit(1).to_list(length=None)

    async def add(self, history_data: dict):
        """Add a new history document to the collection."""
        result = await self.history_collection.insert_one(history_data)
        return str(result.inserted_id)

    async def update(self, conversation_id: str, user_id: str, updated_data: dict):
        """Update an existing history document."""
        await self.history_collection.update_one(
            {"conversation_id": conversation_id, "user_id": user_id},
            {"$set": updated_data}
        )

    async def delete(self, conversation_id: str, user_id: str):
        """Delete a history document."""
        await self.history_collection.delete_one({"conversation_id": conversation_id, "user_id": user_id})

    async def get_all(self, query=None, sort_field: str = None, sort_order: int = -1, limit: int = None):
        """
        Fetch documents from the history collection with optional sorting and limiting.
        """
        if query is None:
            query = {}
        cursor = self.history_collection.find(query)

        if sort_field:
            cursor = cursor.sort(sort_field, sort_order)

        if limit:
            cursor = cursor.limit(limit)

        return await cursor.to_list(length=None)

    async def get_distinct_conversation_ids(self, filter_criteria: dict):
        return await self.history_collection.distinct("conversation_id", filter_criteria)

    async def aggregate(self, pipeline: list):
        """Execute an aggregation pipeline on the history collection."""
        return self.history_collection.aggregate(pipeline)
