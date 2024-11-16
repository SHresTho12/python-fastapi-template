from typing import Dict
import asyncio

from auth import AuthRepo
from config import logger, get_settings
from core.repository.base_repository import BaseRepo
from core.const import GROUP_LIST, MODULE_LIST, GROUP_LIST_REVERSE
from permission.repository.group import GroupRepo
from permission.repository.module import ModuleRepo


class InitializeData:
    def __init__(self):
        self.module_repo: BaseRepo = ModuleRepo()
        self.group_repo: BaseRepo = GroupRepo()
        self.group_list: Dict = GROUP_LIST
        self.module_list: Dict = MODULE_LIST

    async def start_initialize_data(self):
        logger.debug("Started insert initialize data!")
        await asyncio.gather(*[
            asyncio.create_task(self.group_initialize_data_insert()),
            asyncio.create_task(self.module_initialize_data_insert()),
        ])
        logger.debug("Successfully Insert initialize data!")

    async def group_initialize_data_insert(self):
        db_groups = []
        for key, value in self.group_list.items():
            exist_data = None
            async with self.group_repo:
                exist_data = await self.group_repo.get(
                    filters=(
                        self.group_repo._model.id == key,
                        self.group_repo._model.name == value,
                    )
                )
            if not exist_data:
                db_groups.append(self.group_repo._model(id=key, name=value, is_protected=True))

        if db_groups:
            async with self.group_repo:
                self.group_repo._session.add_all(db_groups)
                await self.group_repo._session.commit()
        await self.insert_initialize_super_user()

    async def module_initialize_data_insert(self):
        db_modules = []
        for key, value in self.module_list.items():
            async with self.module_repo:
                exist_data = await self.module_repo.get(
                    filters=(
                        self.module_repo._model.id == key,
                        self.module_repo._model.name == value,
                    )
                )
            if not exist_data:
                db_modules.append(self.module_repo._model(id=key, name=value))
        if db_modules:
            async with self.module_repo:
                self.module_repo._session.add_all(db_modules)
                await self.module_repo._session.commit()

    async def insert_initialize_super_user(self):
        user_repo = AuthRepo()
        async with user_repo:
            exist_data = await user_repo.get(
                filters=(
                    user_repo._model.email == get_settings().super_user_email,
                )
            )
        if not exist_data:
            async with self.group_repo:
                super_user_group = await self.group_repo.get(
                    filters=(
                        self.group_repo._model.id == GROUP_LIST_REVERSE['Super Admin'],
                    )
                )
            password = user_repo.get_password_hash(get_settings().super_user_password)
            async with user_repo:
                await user_repo.create({
                    'email': get_settings().super_user_email,
                    'password': password,
                    'groups': [super_user_group]
                })


initialize_data = InitializeData()
