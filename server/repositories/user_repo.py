from datetime import datetime

from connection.database_conn import init_db
from models.auth_model import SuperAdmin
from models.user_model import Agent


class UserRepo:
    def __init__(self):
        self.db = init_db()
        self.user_collection = self.get_user_collection()
        self.create_indexes()

    def get_user_collection(self):
        return self.db.get_collection("users")

    def create_indexes(self):
        self.user_collection.create_index("user_name", unique=True)

    async def get_user(self, query=None, projection=None):
        if query is None:
            query = {}
        return await self.user_collection.find_one(query, projection)

    async def get_all_users(self, query=None, projection=None, limit=None, offset=None):
        if query is None:
            query = {}

        cursor = self.user_collection.find(query, projection)

        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        return await cursor.to_list(None)

    async def add_user(self, user, session = None) -> Agent:
        user =  await self.user_collection.insert_one(user.dict(), session=session)

        # Get the inserted user
        inserted_user = await self.user_collection.find_one({"_id": user.inserted_id})
        return Agent(**inserted_user)

    async def update_user(self, query, update, session = None):
        return await self.user_collection.update_one(query, update, session=session)


class AdminRepo:
    def __init__(self):
        self.db = init_db()
        self.admin_collection = self.get_admin_collection()
        self.create_indexes()

    def get_admin_collection(self):
        return self.db.get_collection("admins")

    def create_indexes(self):
        self.admin_collection.create_index("email", unique=True)

    async def get_admin(self, query=None, projection=None):
        if query is None:
            query = {}
        return await self.admin_collection.find_one(query, projection)

    async def add_admin(self, admin, session = None):
        admin = await self.admin_collection.insert_one(admin.dict(), session=session)
        # Get the inserted user
        inserted_admin = await self.admin_collection.find_one({"_id": admin.inserted_id})
        return SuperAdmin(**inserted_admin)

    async def update_admin(self, query, update, session = None):
        return await self.admin_collection.update_one(query, update, session=session)

    async def get_admin_count(self, query=None):
        if query is None:
            query = {}
        return await self.admin_collection.count_documents(query)

    async def delete_admin(self, query, session = None):
        return await self.admin_collection.delete_one(query, session=session)

    async def get_all_admins(self, query=None, projection=None, limit=None, offset=None):
        if query is None:
            query = {}

        cursor = self.admin_collection.find(query, projection)

        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        return await cursor.to_list(None)


class AgentRepo:
    def __init__(self):
        self.db = init_db()
        self.registered_agent_collection = self.get_registered_agent_collection()
        self.create_indexes()

    def get_registered_agent_collection(self):
        return self.db.get_collection("registered_agents")

    def create_indexes(self):
        self.registered_agent_collection.create_index("agent_id", unique=True)

    async def find_registered_agent(self, query=None):
        if query is None:
            query = {}
        return await self.registered_agent_collection.find_one(query) is not None

    async def get_agent(self, query=None, projection=None):
        if query is None:
            query = {}
        return await self.registered_agent_collection.find_one(query, projection)

    async def register_agent(self, user, session=None):
        agent = await self.registered_agent_collection.insert_one(user.dict(), session=session)

        inserted_agent = await self.registered_agent_collection.find_one({"_id": agent.inserted_id})
        return Agent(**inserted_agent)

    async def update_agent(self, query, update, session = None):
        return await self.registered_agent_collection.update_one(query, update, session=session)

    async def get_agent_count(self, query=None):
        if query is None:
            query = {}
        return await self.registered_agent_collection.count_documents(query)

    async def get_all_agents(self, query=None, projection=None, limit=None, offset=None):
        if query is None:
            query = {}

        cursor = self.registered_agent_collection.find(query, projection)

        if offset is not None:
            cursor = cursor.skip(offset)
        if limit is not None:
            cursor = cursor.limit(limit)

        return await cursor.to_list(None)
