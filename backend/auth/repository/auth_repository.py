import json
import pyseto
from pyseto import Key
from typing import Optional, Tuple, Union, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload, contains_eager

from core.repository.base_repository import BaseRepo, ModelType
from passlib.context import CryptContext
from datetime import date, datetime, timedelta
from fastapi import HTTPException, status, BackgroundTasks

from core.const import GROUP_LIST_REVERSE
from core.enums import MailSendType, Status
from auth import (
    User,
    UserSignUPBase,
    UserLogin,
    LoginResponse,
    ResetPassword,
    ForgetPassword, PasswordChange
)
from config import get_settings, logger

from core.email import send_email
from core.utils import decoding_token
from permission.repository.group import GroupRepo
from user_info.service.user_information import UserInformationService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class AuthRepo(BaseRepo):
    def __init__(self) -> None:
        super(AuthRepo, self).__init__(
            _model=User,
        )

    async def list(
            self, filters: Optional[Tuple] = (), limit: Optional[int] = None
    ) -> List[ModelType]:
        try:
            statement = select(self._model).join(self._model.groups, isouter=True).options(
                joinedload("groups"),
                contains_eager(self._model.groups)
            ).where(*filters)
            result = await self._session.execute(statement)
            data = result.unique().scalars().all()
            return data
        except Exception as e:
            raise e

    async def get(self, filters: Optional[Tuple] = ()) -> Union[ModelType, None]:
        try:
            statement = select(self._model).options(
                joinedload(self._model.groups)
            ).where(*filters)
            result = await self._session.execute(statement)
            data = result.scalars().first()
            return data
        except Exception as e:
            raise e

    async def sign_up_user(
            self,
            user_sign_up_data: UserSignUPBase,
            background_tasks: BackgroundTasks
    ):
        if await self.get(
                filters=(
                        self._model.email == user_sign_up_data.email,
                )
        ):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="User with this email address already exists",
            )
        from core.utils import phone_number_validation_check
        await phone_number_validation_check(user_sign_up_data)
        user_sign_up_data.email = user_sign_up_data.email.lower()
        user_sign_up_data.password = self.get_password_hash(user_sign_up_data.password)
        user_sign_up_data = user_sign_up_data.__dict__
        group_repo = GroupRepo()
        async with group_repo:
            group_data = await group_repo.get(
                filters=(
                    group_repo._model.id == GROUP_LIST_REVERSE['Admin'],
                )
            )
        user_sign_up_data.update({
            "status": Status.INACTIVE.value,
            "groups": [group_data]
        })
        user: User = await self.create(user_sign_up_data)
        user_information = UserInformationService()
        await user_information.signup_time_create_user(user)
        try:
            background_tasks.add_task(
                send_email,
                email=user.email,
                type=MailSendType.VERIFICATION.value,
                id=user.id
            )
        except:
            logger.error("Something went wrong. Mail does not send", exc_info=1)
        return user

    async def sign_up_verification(self, token: str):
        user = await self.token_validation_check(token, MailSendType.VERIFICATION.value)
        if user.status == Status.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already verified. Please Login!"
            )
        data = {
            "status": Status.ACTIVE.value
        }
        await self.update(user, data)
        return "Your email address has been successfully verified!"

    async def resend_verification_email(
            self,
            email: str,
            background_tasks: BackgroundTasks
    ):
        user = await self.get(
            filters=(
                self._model.email == email,
            )
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This email user does not exist in our system. Please sign up!"
            )
        if user.status == Status.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already verified!"
            )
        try:
            background_tasks.add_task(
                send_email,
                email=user.email,
                type=MailSendType.VERIFICATION.value,
                id=user.id
            )
        except:
            logger.error("Something went wrong", exc_info=1)
        return "Please check email to verify your account!"

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str):
        user = await self.get(
            filters=(
                self._model.email == email,
            )
        )
        if not user:
            return False
        if user.status != Status.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account not verified, Please verify your account!",
            )
        if not self.verify_password(password, user.password):
            return False
        return user

    async def create_access_token(self, user):
        expire = datetime.utcnow() + timedelta(minutes=get_settings().access_token_expire_minutes)
        user_data = {}
        user_data.update({
            "id": user.id,
            "email": user.email
        })
        token_data = {}
        token_data.update({"data": user_data, "token_type": "bearer", "exp": expire})
        user_token_data = json.dumps(token_data, default=json_serial).encode('utf-8')
        local_key = Key.new(version=4, purpose="local", key=get_settings().paseto_local_key)
        token = pyseto.encode(local_key, user_token_data)
        return token.decode(), expire

    async def create_refresh_token(self, user):
        expire = datetime.utcnow() + timedelta(minutes=get_settings().refresh_token_expire_minutes)
        user_data = {}
        user_data.update({
            "id": user.id,
            "email": user.email
        })
        token_data = {}
        token_data.update({"data": user_data, "token_type": "bearer", "exp": expire})
        user_token_data = json.dumps(token_data, default=json_serial).encode('utf-8')
        local_key = Key.new(version=4, purpose="local", key=get_settings().paseto_local_key)
        token = pyseto.encode(local_key, user_token_data)
        return token.decode()

    async def login(self, login_user: UserLogin):
        user: User = await self.authenticate_user(
            login_user.email.lower(),
            login_user.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token, exp = await self.create_access_token(user)
        refresh_token = await self.create_refresh_token(user)
        response_data = LoginResponse(
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expiry_time=f"{exp}"
        )
        return response_data

    async def token_validation_check(self, token: str, type: int):
        payload = decoding_token(token)

        try:
            id = int(payload.get('id', None))
        except:
            id = None
        try:
            token_type = int(payload.get('type', None))
        except:
            token_type = None

        user = None
        if id:
            user = await self.get(
                filters=(
                    self._model.id == id,
                )
            )
        if token_type != type or not user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token!"
            )
        return user

    async def reset_password(self, token: str, reset_password: ResetPassword):
        user = await self.token_validation_check(token, MailSendType.PASSWORD_RESET.value)
        meta = user.meta if user.meta else {}
        if meta.get('password_reset', None) == "On_going":
            update_data = reset_password.dict(exclude_unset=True)
            hashed_password = self.get_password_hash(update_data["new_password"])
            if update_data["new_password"] != update_data["confirm_password"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password and confirm password are not same!"
                )
            meta.update({
                'password_reset': 'Done'
            })
            data = {
                "password": hashed_password,
                "meta": meta
            }
            await self.update(user, data)
            return {"Password successfully reset!"}
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token is expired"
            )


    async def password_changed(
            self,
            current_user: "Users",
            changed_password: PasswordChange
    ):
        update_data = changed_password.dict(exclude_unset=True)
        hashed_password = self.get_password_hash(update_data["new_password"])
        if update_data["new_password"] != update_data["confirm_password"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password are not same!"
            )
        if not self.verify_password(update_data['old_password'], current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid old password!"
            )
        data = {
            "password": hashed_password
        }
        await self.update(current_user, data)
        return {"Password successfully updated!"}




    async def forget_password(
            self,
            email: ForgetPassword,
            background_tasks: BackgroundTasks
    ):
        user = await self.get(
            filters=(
                self._model.email == email.email,
            )
        )
        if not user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="This email user does not exist in our system. Please sign up!"
            )
        meta = user.meta if user.meta else {}
        meta['password_reset'] = "On_going"
        await self.update(user, {'meta': meta})
        try:
            background_tasks.add_task(
                send_email,
                email=user.email,
                type=MailSendType.PASSWORD_RESET.value,
                id=user.id
            )
        except:
            logger.error("Something went wrong. Mail does not send", exc_info=1)
        return "Please check your email to reset password!"

    async def get_user_from_refresh_token(self, refresh_token):
        try:
            local_key = Key.new(version=4, purpose="local", key=get_settings().paseto_local_key)
            decoded = pyseto.decode(local_key, refresh_token)
            payload = decoded.payload.decode()
            payload = json.loads(payload)
        except:
            payload = {}
        data = payload.get('data', {})
        id = data.get('id', None)
        email = data.get('email', None)
        if not id or not email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid refresh token!"
            )
        user = await self.get(
            filters=(
                self._model.email == email,
                self._model.id == id
            )
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid refresh token or token is expired!"
            )
        access_token, exp = await self.create_access_token(user)
        refresh_token = await self.create_refresh_token(user)
        response_data = LoginResponse(
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expiry_time=f"{exp}"
        )
        return response_data


