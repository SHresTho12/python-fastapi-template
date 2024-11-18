import http
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from Token_verifier.auth import verify_api_token, verify_access_token
from core.config import get_config
from constants.auth_consts import SUPER_ADMIN_ROLE
from models.auth_model import UserLogin, LoginResponse, SuperAdmin, RefreshTokenReq, \
    AddNewMemberPayload
from models.user_model import Agent
from services.auth_service import AuthService
from utils.user_utils import UserUtils

auth_router = APIRouter()
config = get_config()
@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=http.HTTPStatus.OK
)
async def login(user_info: UserLogin):
    auth_service = AuthService()
    response = await auth_service.login(user_info)
    return response

@auth_router.post(
    "/create-super-admin",
    status_code=http.HTTPStatus.CREATED,
    response_model=SuperAdmin,
    dependencies=[Depends(verify_api_token)]
)
async def create_super_admin(super_admin: Optional[SuperAdmin]= None):
    auth_service = AuthService()
    if super_admin is None:
        super_admin = SuperAdmin(
            email=config.super_admin_email,
            password=config.super_admin_password,
        )
    response = await auth_service.create_super_admin(super_admin)
    return response

@auth_router.post(
    "/refresh-token",
    response_model=LoginResponse,
    status_code=http.HTTPStatus.OK
)
async def refresh_token(token: RefreshTokenReq):
    auth_service = AuthService()
    response = await auth_service.verify_refresh_token(token.refresh_token)
    return response

@auth_router.post(
    "/register-agent",
    status_code=http.HTTPStatus.CREATED
)
async def register_agent(agent: Agent):
    auth_service = AuthService()
    return await auth_service.register_agent(agent)

@auth_router.post(
    "/add-new-member-role",
    status_code=http.HTTPStatus.CREATED,
    dependencies=[Depends(verify_access_token)]
)
async def add_new_member(
        member: AddNewMemberPayload,
        token_payload: dict = Depends(verify_access_token)
):
    UserUtils.check_for_super_admin_privilege(token_payload)
    if member.role == SUPER_ADMIN_ROLE:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail="Super admin can't be added"
        )
    auth_service = AuthService()
    return await auth_service.add_new_member(member)
