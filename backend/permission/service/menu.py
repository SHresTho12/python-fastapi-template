from typing import Any

from fastapi import HTTPException, status

from core.const import GROUP_LIST_REVERSE
from core.enums import MenuType, PermissionType
from core.utils import get_all_api_endpoint
from permission.repository.menu import MenuRepo
from permission.repository.module import ModuleRepo
from permission.repository.permission import PermissionRepo
from permission.schema.menu import MenuView

from core.service.base_service import BaseService, ModelType


class MenuService(BaseService):
    def __init__(self):
        self.repository = MenuRepo()
        self.read_schema = MenuView
        super().__init__(
            repository=self.repository,
            read_schema=self.read_schema
        )

    async def _validate(self, data, record_id: int | None = None):
        filters = (
            self.repository._model.api_end_point == data.api_end_point,
            self.repository._model.module_id == data.module_id,
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

    async def find_root_parent(self, parent_id):
        async with self.repository:
            menu_data = await self.repository.get(
                filters=(
                    self.repository._model.id == id,
                )
            )
        if menu_data.menu_type == MenuType.PARENT.value:
            return parent_id
        return await self.find_root_parent(menu_data.parent_menu)

    async def check_data_validation(self, menu_data):
        module_repo = ModuleRepo()
        module = None
        async with module_repo:
            module = await module_repo.get(
                filters=(
                    module_repo._model.id == menu_data.module_id,
                )
            )
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="module data not found"
            )

        if menu_data.menu_type == MenuType.CHILD.value:
            if menu_data.parent_menu:
                async with self.repository:
                    parent = await self.repository.get(
                        filters=(
                            self.repository._model.id == menu_data.parent_menu,
                        )
                    )
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="parent data not found"
                    )
                if parent.module_id != menu_data.module_id:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Parent and child module are not same"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Parent filed missing. Please insert parent data"
                )
        return True

    async def create_menu(self, request, current_user, data: dict | Any) -> MenuView:
        await self.check_data_validation(data)
        if data.menu_type == MenuType.PARENT.value:
            data.parent_menu = None
        if data.api_end_point is not None and data.api_end_point.strip():
            api_end_point_set, url_method_dict = get_all_api_endpoint(request)
            api_end_point_list = list(api_end_point_set)
            if data.api_end_point not in api_end_point_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid api end point"
                )
        response = await self.insert(data, current_user)
        permission_repo = PermissionRepo()
        async with permission_repo:
            await permission_repo.create({
                "group_id": GROUP_LIST_REVERSE['Super Admin'],
                "menu_id": response.id,
                "permission_type": PermissionType.ALL_DATA.value
            })
        return response


    async def update_menu(self, id, request, updated_data, current_user) -> MenuView:
        if updated_data.menu_type == MenuType.PARENT.value:
            updated_data.parent_menu = None
        await self.check_data_validation(updated_data)
        menu_data = await self.get_db_obj(record_id=id)
        if updated_data.menu_type == MenuType.CHILD.value or updated_data.menu_type == MenuType.PERMISSION.value:
            if menu_data.menu_type == MenuType.PARENT.value and updated_data.menu_type != MenuType.PERMISSION.value:
                parent_id = await self.find_root_parent(updated_data.parent_menu)
                if parent_id == id:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Circular error of this input.Please insert other parent",
                    )
            elif menu_data.menu_type == MenuType.CHILD.value or updated_data.menu_type == MenuType.PERMISSION.value:
                if menu_data.parent_menu != updated_data.parent_menu:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Already child in this menu.",
                    )
        else:
            updated_data.parent_menu = None
        if updated_data.api_end_point is not None and updated_data.api_end_point.strip():
            api_end_point_set, url_method_dict = get_all_api_endpoint(request)
            api_end_point_list = list(api_end_point_set)
            if updated_data.api_end_point not in api_end_point_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invalid api end point"
                )
        response = await self.edit(id, updated_data, current_user)
        return response
    async def delete_menu(
            self,
            record_id: Any,
            current_user: ModelType | None = None
    ):
        permission_repo = PermissionRepo()
        async with permission_repo:
            await permission_repo.hard_delete(
                filters=(
                    permission_repo._model.menu_id == record_id,
                )
            )
        await self.delete(record_id, current_user)


