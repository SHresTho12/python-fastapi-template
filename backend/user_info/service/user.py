from typing import Type
from fastapi import HTTPException, status,Depends

from auth import User
from core.security import pwd_context
from core.service.base_service import BaseService
from permission.repository.group import GroupRepo
from permission.service.group import GroupService
from user_info.repository.user import UserRepo
from user_info.schema.user import UserView, UserCreate, UserEdit


class UserService(BaseService):
    def __init__(
        self,
        repository: UserRepo = Depends(UserRepo),
        read_schema: Type[UserView] = UserView,
    ):
        super().__init__(repository=repository, read_schema=read_schema)

    async def _validate(self, data, record_id: int | None = None):
        filters = (
            self.repository._model.email == data.email,
            self.repository._model.deleted_at == None
        )
        if record_id:
            filters = filters + (
                self.repository._model.id != record_id,
            )
        async with self.repository:
            exist_data = await self.repository.get(
                filters=filters
            )
        if exist_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Already exist this data!"
            )

    async def add_group(self, schema_data: UserCreate | UserEdit):
        group_service = GroupService()
        group_data = await group_service.get_db_obj(schema_data.group_id)
        data = schema_data.__dict__
        del data['group_id']
        data['groups'] = [group_data]
        return data

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def insert(
            self,
            create_schema: UserCreate,
            current_user: User | None = None
    ):
        await self._validate(create_schema)
        hashed_password = self.get_password_hash(create_schema.password)
        create_data = await self.add_group(create_schema)
        create_data['password'] = hashed_password
        return await self._insert(create_data, current_user)

    async def edit(
            self,
            record_id: int,
            update_schema: UserEdit,
            current_user: User | None = None
    ) -> UserView:
        update_data = await  self.add_group(update_schema)
        return await self._edit(record_id, update_data, current_user)
