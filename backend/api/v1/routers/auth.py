from typing import Optional

from fastapi import APIRouter, Depends, status, Request, BackgroundTasks

from auth import UserLogin, ForgetPassword, ResetPassword, RefreshToken, RefreshTokenResponse, LoginResponse, \
    PasswordChange
from auth.repository.auth_repository import AuthRepo
from auth.schema.user_schema import UserSignUPBase
from core.common_base import BaseResponse
from core.utils import request_user, get_all_status
from permission.service.permission import PermissionService

auth_router = r = APIRouter()


@r.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
        user: UserSignUPBase,
        background_tasks: BackgroundTasks
):
    auth_repo = AuthRepo()
    async with auth_repo:
        db_user_org = await auth_repo.sign_up_user(user, background_tasks)
    return "Please check email to verify your account!"


@r.post("/resend-email/{email}")
async def resend_verification_email(
        email: str,
        background_tasks: BackgroundTasks,
):
    auth_repo = AuthRepo()
    async with auth_repo:
        message = await auth_repo.resend_verification_email(email, background_tasks)
    return message


@r.get(
    '/verification/{token}',
    status_code=status.HTTP_201_CREATED
)
async def sign_up_verification(
        token: str
):
    auth_repo = AuthRepo()
    async with auth_repo:
        message = await auth_repo.sign_up_verification(token)
    return message


@r.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED
)
async def login(
        user: UserLogin
):
    auth_repo = AuthRepo()
    async with auth_repo:
        response = await auth_repo.login(user)
    return response


@r.get("/login_permissions")
async def user_permission(
        request: Request,
        module_id: Optional[int] = 0,
        current_user=Depends(request_user)
):
    """
    Get user all permission
    """
    permission_service = PermissionService()
    return BaseResponse(
        code=status.HTTP_200_OK,
        msg="Fetched successfully!",
        data=await permission_service.get_permissions_by_user_login(request, current_user, module_id)
    )


@r.post(
    '/forget_password',
    status_code=status.HTTP_201_CREATED
)
async def forget_password(
        forget_password: ForgetPassword,
        background_tasks: BackgroundTasks
):
    auth_repo = AuthRepo()
    async with auth_repo:
        message = await auth_repo.forget_password(forget_password, background_tasks)
    return message


@r.patch(
    '/reset_password/{token}',
    status_code=status.HTTP_201_CREATED
)
async def reset_password(
        token: str,
        reset_password: ResetPassword,
):
    auth_repo = AuthRepo()
    async with auth_repo:
        message = await auth_repo.reset_password(token, reset_password)
    return message


@r.post(
    "/refresh-token",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def refresh_token(
        refresh_token: RefreshToken
):
    auth_repo = AuthRepo()
    async with auth_repo:
        message = await auth_repo.get_user_from_refresh_token(refresh_token.refresh_token)
    return message

@r.patch(
    '/changed_password',
    status_code=status.HTTP_201_CREATED
)
async def changed_password(
        changed_password: PasswordChange,
        current_user=Depends(request_user)
):
    auth_repo = AuthRepo()
    async with auth_repo:
        message = await auth_repo.password_changed(
            current_user, changed_password)
    return message