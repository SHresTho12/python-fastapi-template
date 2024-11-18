import http
from typing import Optional

from fastapi import APIRouter, Query, Depends
from fastapi.params import Query

from Token_verifier.auth import verify_access_token
from models.user_model import AgentListResponse, ConversationResponse, AdminListResponse, UpdateAdminRoleRequest, Agent
from services.auth_service import AuthService
from services.user_service import UserService
from utils.user_utils import UserUtils

user_router = APIRouter()

@user_router.get(
    "/get-agents",
    status_code=http.HTTPStatus.OK,
    response_model=AgentListResponse,
    dependencies=[Depends(verify_access_token)]
)
async def get_agents(
    limit: Optional[int] = Query(10, description="Number of agents to retrieve"),
    offset: Optional[int] = Query(0, description="Number of agents to skip"),
    name: Optional[str] = Query(None, description="Name of the agent to search")
):
    """Retrieve a list of agents."""
    user_service = UserService()
    agents_list = await user_service.get_agents(limit, offset, name)
    return agents_list

@user_router.get(
    "/is-already-registered",
    status_code=http.HTTPStatus.OK
)
async def is_already_registered(user_name: str = Query(..., description="User name to check if already registered")):
    user_service = UserService()
    already_registered=await user_service.is_already_registered(user_name)
    return {"already_registered": already_registered}

@user_router.get(
    "/get-admins",
    status_code=http.HTTPStatus.OK,
    response_model=AdminListResponse,
    dependencies=[Depends(verify_access_token)]
)
async def get_admins(
    limit: Optional[int] = Query(10, description="Number of admins to retrieve"),
    offset: Optional[int] = Query(0, description="Number of admins to skip"),
    name: Optional[str] = Query(None, description="Name of the admin to search"),
    token_payload: dict = Depends(verify_access_token)
):
    """Retrieve a list of admins."""
    UserUtils.check_for_super_admin_privilege(token_payload) # Check if the user is a super admin
    user_service = UserService()
    admins_list = await user_service.get_admins(limit, offset, name)
    return admins_list

@user_router.post(
    "/update-admin-role",
    status_code=http.HTTPStatus.OK,
    dependencies=[Depends(verify_access_token)]
)
async def update_admin_role(admin: UpdateAdminRoleRequest, token_payload: dict = Depends(verify_access_token)):
    UserUtils.check_for_super_admin_privilege(token_payload)
    user_service = UserService()
    return await user_service.update_admin_role(admin.user_id, admin.role)

@user_router.delete(
    "/delete-admin",
    status_code=http.HTTPStatus.OK,
    dependencies=[Depends(verify_access_token)]
)
async def delete_admin(Id : str= Query(..., description= " Id to be deleted"), token_payload: dict = Depends(verify_access_token)):
    UserUtils.check_for_super_admin_privilege(token_payload)
    user_service =UserService()
    return await user_service.delete_admin(Id)
