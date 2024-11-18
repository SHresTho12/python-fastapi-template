import http
import logging
from datetime import datetime, timedelta
from typing import Dict

import jwt
from fastapi import HTTPException

from jwt import PyJWTError

from Token_verifier.auth import verify_refresh_token
from core.config import get_config
from constants.auth_consts import AGENT_ROLE
from models.auth_model import UserLogin, LoginResponse, SuperAdmin, AddNewMemberPayload
from models.user_model import Agent
from repositories.statistics_repo import StatisticsRepo
from repositories.user_repo import AdminRepo, AgentRepo
from passlib.context import CryptContext

from pymongo import errors

# Initialize the CryptContext with bcrypt as the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = get_config()

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.agent_repo = AgentRepo()
        self.admin_repo = AdminRepo()
        self.statistics_repo = StatisticsRepo()
        self.access_token_expire = config.access_token_expire
        self.refresh_token_expire = config.refresh_token_expire
        self.access_token_secret = config.access_token_secret_key
        self.refresh_token_secret = config.refresh_token_secret_key
        self.jwt_algorithm = config.jwt_algorithm

    async def login(self, user_info: UserLogin) -> LoginResponse:
        user = await self.admin_repo.get_admin({"email": user_info.email})
        if not user :
           raise HTTPException(
               status_code= http.HTTPStatus.UNAUTHORIZED,
               detail="Invalid credentials",
               headers={"WWW-Authenticate": "Bearer"}
           )

        if not self.verify_password(user_info.password, user.get("password")):
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Generate a JWT token
        access_token = await self.get_access_token(user)
        refresh_token = await self.get_refresh_token(user)
        response_data = LoginResponse(
            email=user.get("email"),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        return response_data

    async def create_super_admin(self, super_admin: SuperAdmin) -> SuperAdmin:
        super_admin_exists = await self.admin_repo.get_admin({"email": super_admin.email})
        if super_admin_exists:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="User with this email already exists"
            )
        super_admin.password = self.hash_password(super_admin.password)
        super_admin.created_at = datetime.utcnow()
        super_admin.updated_at = datetime.utcnow()

        return await self.admin_repo.add_admin(super_admin)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    # Function to verify a password against a hash
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def generate_jwt_token(self, user: Dict[str, str], expire: int, secret_key:str) -> str:
        try:
            expire = datetime.utcnow() + timedelta(seconds=expire)
            user_data = {
                "user_id": str(user.get("_id")),
                "email": user.get("email"),
                "role": user.get("role"),
            }
            # Encode JWT token
            token = jwt.encode(
                {"exp": expire, "data": user_data},
                secret_key,
                algorithm=self.jwt_algorithm
            )
            return token
        except PyJWTError as e:
            print("JWT generation error:", e)
            return ""

    async def get_access_token(self, user: Dict[str, str]) -> str:
        return await self.generate_jwt_token(user, self.access_token_expire, self.access_token_secret)

    async def get_refresh_token(self, user: Dict[str, str]) -> str:
        return await self.generate_jwt_token(user, self.refresh_token_expire, config.refresh_token_secret_key)

    async def verify_refresh_token(self, refresh_token: str) -> LoginResponse:
        refresh_token = verify_refresh_token(refresh_token)
        if not refresh_token:
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        refresh_token= refresh_token['data']
        user = {
            "user_id": refresh_token.get("user_id"),
            "email": refresh_token.get("email"),
            "role": refresh_token.get("role")
        }
        access_token = await self.get_access_token(user)
        refresh_token = await self.get_refresh_token(user)
        response_data = LoginResponse(
            email=user["email"],
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        return response_data

    async def register_agent(self, agent:Agent):
        if await self.agent_repo.get_agent({"user_name": agent.user_name}):
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Agent with this user name is already registered"
            )
        agent.created_at = datetime.utcnow()
        agent.updated_at = datetime.utcnow()
        agent.role = AGENT_ROLE

        result = await self.agent_repo.register_agent(agent)

        await self.statistics_repo.update({}, {"$inc": {"total_customer_agents": 1}})
        return result

    async def add_new_member(self, member: AddNewMemberPayload):
        user = await self.admin_repo.get_admin({"email": member.email})
        if user and user.get("role") == member.role:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=f"This person is already added as {member.role}"
            )

        member.password = self.hash_password(member.password)
        member.created_at = datetime.utcnow()
        member.updated_at = datetime.utcnow()

        try:
            await self.admin_repo.add_admin(member)
        except errors.PyMongoError:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error adding new member as: {member.role}"
            )
        return {"message": f"New member added successfully as {member.role}"}
