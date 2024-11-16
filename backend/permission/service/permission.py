from typing import Any, List, Dict

from fastapi import HTTPException, status
from sqlalchemy import or_, text

from core.const import GROUP_LIST_REVERSE
from core.enums import Status
from core.utils import get_all_api_endpoint
from permission import Permission
from permission.repository.group import GroupRepo
from permission.repository.menu import MenuRepo
from permission.repository.module import ModuleRepo
from permission.repository.permission import PermissionRepo
from permission.schema.permission import PermissionOperation, PermissionMenuView


class PermissionService:
    def __init__(self):
        self.repository = PermissionRepo()
        self.menu_repo = MenuRepo()
        self.group_repo = GroupRepo()
        self.module_repo = ModuleRepo()
        self._model = Permission

    async def get_group_data(self, group_id):
        async with self.group_repo:
            group_data = await self.group_repo.get(
                filters=(
                    self.group_repo._model.id == group_id,
                )
            )
        if not group_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group data not found!"
            )
        return group_data

    async def get_module_data(self, module_id):

        async with self.module_repo:
            module_data = await self.module_repo.get(
                filters=(
                    self.module_repo._model.id == module_id,
                    self.module_repo._model.id == module_id,
                )
            )
        if not module_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module data not found!"
            )
        return module_data

    async def set_group_based_permission(
            self,
            request,
            permission_data: dict | Any
    ):
        await self.get_group_data(permission_data.group_id)
        data = permission_data.dict(exclude_unset=True)
        permission_update_list = []
        permission_list = []
        menu_dict = {}

        # Retrieve API endpoints and methods
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        for menu in data['menu_permission']:
            # Fetch menu data using the helper function
            menu_data = await self.__fetch_menu_data(menu['id'])

            if not menu_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"This {menu['id']}'s id dose not add in this permission"
                )
            # Fetch existing permission data using the helper function
            existing_permission = await self.__fetch_existing_permission(permission_data.group_id, menu_data.id)

            action_dict = PermissionOperation(**menu).dict()['action']
            for action in action_dict.keys():
                if action not in url_method_dict.get(menu_data.api_end_point, {}):
                    menu['action'][str(action)] = False
            menu_id = menu.pop('id')
            menu.update({
                'status': Status.ACTIVE.value,
                'group_id': data['group_id'],
                'menu_id': menu_id
            })
            menu_dict[str(menu_data.id)] = menu_data

            if existing_permission:
                permission_update_list.append((existing_permission, menu))
            else:
                permission_list.append(self._model(**menu))

        # Perform database operations
        async with self.repository:
            if permission_list:
                self.repository._session.add_all(permission_list)
                await self.repository._session.flush()
            for perm, updated_data in permission_update_list:
                await self.repository.update(perm, updated_data, is_add= False, is_commit=False)
            await self.repository._session.commit()

        return {"detail": "Successfully set Permissions"}

    async def __fetch_menu_data(self, menu_id: int):
        async with self.menu_repo:
            return await self.menu_repo.get(
                filters=(
                    self.menu_repo._model.id == menu_id,
                    self.menu_repo._model.status == Status.ACTIVE.value,
                    self.menu_repo._model.deleted_at.is_(None)
                )
            )

    async def __fetch_existing_permission(self, group_id: int, menu_id: int):
        async with self.repository:
            return await self.repository.get(
                filters=(
                    self._model.group_id == group_id,
                    self._model.menu_id == menu_id,
                    self._model.deleted_at.is_(None)
                )
            )

    async def get_group_based_permission(
            self,
            request,
            group_id,
            module_id

    ) -> List[PermissionMenuView]:

        group_data = await self.get_group_data(group_id)
        filters = (
            self.menu_repo._model.status == Status.ACTIVE.value,
        )
        if module_id:
            await self.get_module_data(module_id)
            filters = filters + (
                self.menu_repo._model.module_id == module_id,
            )

        async with self.menu_repo:
            menu_data = await self.menu_repo.list(
                filters=filters
            )
        menu_list = [data.id for data in menu_data]
        api_endpoints, url_methods = get_all_api_endpoint(request)

        all_permissions_dict = {
            data.id: {
                "action": {method: group_data.id == GROUP_LIST_REVERSE['Super Admin'] for method in
                           url_methods.get(data.api_end_point, {})}
            }
            for data in menu_data
        }

        async with self.repository:
            db_permissions = await self.repository.list(
                filters=(
                    self._model.group_id == group_id,
                    self._model.menu_id.in_(menu_list),
                    self._model.deleted_at == None
                )
            )
        for db_permission in db_permissions:
            db_permission_dict = PermissionOperation(**db_permission.__dict__).dict()
            menu_id = db_permission.menu_id
            existing_permissions = all_permissions_dict.get(menu_id, {}).get('action', {})
            updated_permissions = {
                method: db_permission_dict.get(method, False) or existing_permissions.get(method, False)
                for method in set(db_permission_dict) | set(existing_permissions)
            }
            all_permissions_dict[menu_id]['action'] = updated_permissions

        return  [
            PermissionMenuView(
                id=data.id,
                menu_name=data.name,
                module=data.module,
                **all_permissions_dict.get(data.id, {})
            )
            for data in menu_data if all_permissions_dict.get(data.id)
        ]



    async def get_permissions_by_user_login(
            self,
            request,
            current_user,
            module_id: int = None
    ):
        is_superuser = self.__is_superuser(current_user)
        group_type_list = [group.id for group in current_user.groups]

        if not is_superuser:
            async with self.repository:
                permission_subquery = await self.repository.list(
                    filters=(
                        self.__create_json_filter(),
                        self.repository._model.group_id.in_(group_type_list),
                        self.repository._model.deleted_at == None
                    )
                )
            parent_menu_list = set()
            for data in permission_subquery:
                parent_menu_list.add(data.menu_id)
                parent_menu_list.update(await self.__get_all_parent_menu(data.menu))

            filters = self.__build_filters(is_superuser, group_type_list, parent_menu_list, module_id)
        else:
            filters = self.__build_filters(is_superuser, group_type_list, [])

        all_menu_dict, menu_id_list, menu_data_list = await self.__process_permissions(
            filters,
            request,
            is_superuser,
            group_type_list
        )

        db_active_menu = await self.__fetch_active_menus(menu_id_list, module_id)
        active_menu_ids = {data.id for data in db_active_menu}

        module_ids = {data.module_id for data in menu_data_list if data.id in active_menu_ids}
        module_id_list = list(module_ids)  # Convert to list if needed
        db_active_modules = await self.__fetch_active_modules(module_id_list)
        all_module_dict = {module.id: {
            "id": module.id,
            "module_name": module.name,
            "menu_permission": []
        } for module in db_active_modules}

        for data in menu_data_list:
            if data.id in active_menu_ids:
                module_id = data.module_id
                if module_id in all_module_dict:
                    all_module_dict[module_id]['menu_permission'].append(all_menu_dict[data.id])

        specific_permission = []

        for module_id, module in all_module_dict.items():
            module["menu_permission"] = sorted(
                module["menu_permission"], key=lambda _dict: _dict['menu_serial']
            )
            for perm in module["menu_permission"]:
                perm.pop("menu_serial", None)
            specific_permission.append(module)

        return specific_permission

    def __create_json_filter(self):
        return text("EXISTS (SELECT 1 FROM json_each(action) AS kv(key, value) WHERE value::text = 'true')")

    def __is_superuser(self, current_user):
        return any(
            group.id == GROUP_LIST_REVERSE["Super Admin"] for group in current_user.groups
        )

    async def __get_all_parent_menu(self, menu: Any, parent_menu_list: List = []):
        if menu.parent_menu and menu.parent_menu not in parent_menu_list:
            async with self.menu_repo:
                db_parent_menu = await self.menu_repo.get(
                    filters=(
                        self.menu_repo._model.id == menu.parent_menu,
                        self.menu_repo._model.deleted_at.is_(None)
                    )
                )
            parent_menu_list.append(db_parent_menu.id)
            await self.__get_all_parent_menu(db_parent_menu, parent_menu_list)
        return parent_menu_list

    def __build_filters(self, is_superuser, group_type_list, menu_id_list, module_id=None):
        filters = (self.repository._model.deleted_at.is_(None),)
        if not is_superuser:
            filters += (
                or_(
                    self.__create_json_filter(),
                    self.repository._model.menu_id.in_(menu_id_list)
                ),
                self.repository._model.group_id.in_(group_type_list),
                self.repository._model.deleted_at == None
            )
        if module_id:
            filters += (self.menu_repo._model.module_id == module_id,)
        return filters

    async def __process_permissions(self, filters, request, is_superuser, group_type_list):
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        all_menu_dict = {}
        menu_id_list = []
        menu_data_list = []

        async with self.repository:
            all_permission_data = await self.repository.get_permissions_sort_by_menu(filters=filters)
        for data in all_permission_data:
            if data.menu_id not in all_menu_dict:
                menu_id_list.append(data.menu_id)
                menu_data_list.append(data.menu)
                all_menu_dict[data.menu_id] = self.__get_default_login_permission_response_data(data.menu)
            all_menu_dict[data.menu_id] = self.__get_login_permission_response_data(
                is_superuser,
                all_menu_dict[data.menu_id],
                data,
                url_method_dict.get(str(data.menu.api_end_point), {})
            )
        all_menu_dict = {
            menu_id: self.__delete_not_permitted_permissions(menu_dict) for menu_id, menu_dict in all_menu_dict.items()
        }
        return all_menu_dict, menu_id_list, menu_data_list

    async def __fetch_active_menus(self, menu_id_list, module_id):
        filters = (
            self.menu_repo._model.id.in_(menu_id_list),
            self.menu_repo._model.status == Status.ACTIVE.value,
            self.menu_repo._model.deleted_at == None
        )
        if module_id:
            filters += (self.menu_repo._model.module_id == module_id,)

        async with self.menu_repo:
            return await self.menu_repo.get_menus_sort_by_serial(filters=filters)

    async def __fetch_active_modules(self, module_id_list):
        async with self.module_repo:
            return await self.module_repo.list(
                filters=(
                    self.module_repo._model.id.in_(module_id_list),
                    self.module_repo._model.status == Status.ACTIVE.value,
                    self.module_repo._model.deleted_at == None
                )
            )

    def __get_default_login_permission_response_data(self, menu_data):
        return {
            "id": menu_data.id,
            "name": menu_data.name,
            "url": menu_data.menu_url,
            "icon": menu_data.menu_icon,
            "parent_id": menu_data.parent_menu,
            "menu_serial": menu_data.menu_serial,
            "can_create": False,
            "can_edit": False,
            "can_view": False,
            "can_list": False,
            "can_delete": False
        }

    def __get_login_permission_response_data(
            self,
            is_superuser,
            menu_dict,
            data,
            url_method_type: List[str] = []
    ):
        permission_keys = ['create', 'edit', 'view', 'list', 'delete']
        for permission in permission_keys:
            menu_dict[f'can_{permission}'] = (is_superuser or
                                              (permission in url_method_type and data.action.get(permission, False)))
        return menu_dict

    def is_create_permitted(url_method_type: List, is_superuser: bool, action: dict) -> bool:
        pass

    def __delete_not_permitted_permissions(self, menu_dict):
        return {key: value for key, value in menu_dict.items() if value}
