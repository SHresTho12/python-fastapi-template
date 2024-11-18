import http
from datetime import datetime

from fastapi import HTTPException
from pymongo import errors

from models.user_model import AgentResponse, AgentListResponse, AdminListResponse, AdminResponse
from repositories.history_collection import HistoryRepo
from repositories.user_repo import AdminRepo, AgentRepo
from utils.user_utils import UserUtils


class UserService:
    def __init__(self):
        self.agent_repo = AgentRepo()
        self.admin_repo = AdminRepo()
        self.history_repo = HistoryRepo()

    async def get_agents(self, limit: int, offset: int, search_string: str = None) -> AgentListResponse:
        # Create query with optional search filter on full_name or last_name
        query = (
            {"$or": [
                {"full_name": {"$regex": search_string, "$options": "i"}},
            ]}
            if search_string else {}
        )

        # Fetch agents with query, limit, and offset
        agents = await self.agent_repo.get_all_agents(query=query, limit=limit, offset=offset)

        # If no agents found, return an empty AgentListResponse immediately
        if not agents:
            return AgentListResponse(total_agents=0, agents=[])

        # Extract user names from agents
        user_names = [agent.get("user_name") for agent in agents]

        # If no user names, skip aggregation and set latest_timestamps to an empty dictionary
        latest_timestamps = {}
        if user_names:
            # Aggregation pipeline to fetch latest timestamp for each user_name
            pipeline = [
                {"$match": {"user_name": {"$in": user_names}}},
                {"$sort": {"timestamp": -1}},
                {"$group": {
                    "_id": "$user_name",
                    "latest_timestamp": {"$first": "$timestamp"}
                }}
            ]

            # Run aggregation pipeline and build latest_timestamps dictionary
            latest_timestamps = {
                doc["_id"]: doc["latest_timestamp"]
                async for doc in await self.history_repo.aggregate(pipeline)
            }

        # Map each agent to AgentResponse with last_chat_time if available
        agent_responses = [
            AgentResponse(
                user_id=str(agent.get("_id")),
                user_name=agent.get("user_name"),
                agent_name=agent.get("full_name"),
                agent_email=agent.get("email"),
                last_chat_time=latest_timestamps.get(agent.get("user_name"), datetime.min),
                role=agent.get("role")
            )
            for agent in agents
        ]

        # Return AgentListResponse with total count and agent details
        return AgentListResponse(
            total_agents=len(agent_responses),
            agents=agent_responses
        )

    async def get_conversations(self, user_id: str):
        # Fetch all conversations for a user
        conversations = await self.history_repo.get_all(query={"user_id": user_id})

    async def get_admins(self, limit: int, offset: int, search_string: str = None) -> AdminListResponse:
        query = (
            {"$or": [
                {"full_name": {"$regex": search_string, "$options": "i"}},
            ]}
            if search_string else {}
        )

        # Fetch admins with query, limit, and offset
        admins = await self.admin_repo.get_all_admins(query=query, limit=limit, offset=offset)

        # Map each admin to AgentResponse with last_chat_time if available
        admin_responses = [
            AdminResponse(
                user_id=str(admin.get("_id")),
                user_name=admin.get("user_name"),
                email=admin.get("email"),
                role=admin.get("role"),
                created_at=admin.get("created_at"),
                updated_at=admin.get("updated_at")
            )
            for admin in admins
        ]

        # Return AgentListResponse with total count and admin details
        return AdminListResponse(
            total_admins=len(admin_responses),
            admins=admin_responses
        )


    async def is_already_registered(self, user_name: str) -> bool:
        user = await self.agent_repo.get_agent({"user_name": user_name})
        return user is not None


    async def update_admin_role(self, Id: str, role: str):
        object_id = UserUtils.id_to_object_id(Id)

        admin = await self.admin_repo.get_admin({"_id": object_id})
        if not admin:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Admin not found with this email"
            )
        if admin.get("role") == role:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=f"This person is already a {role}"
            )
        try:
            await self.admin_repo.update_admin({"_id": object_id}, {"$set": {"role": role}})
        except errors.PyMongoError:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Error updating admin role"
            )
        return {"message": "Admin role updated successfully"}


    async def delete_admin(self, Id: str):
        object_id = UserUtils.id_to_object_id(Id)

        admin = await self.admin_repo.get_admin({"_id": object_id})
        if not admin:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Admin not found with this email"
            )
        try:
            await self.admin_repo.delete_admin({"_id": object_id})
        except errors.PyMongoError:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Error deleting admin"
            )
        return {"message": "Admin deleted successfully"}