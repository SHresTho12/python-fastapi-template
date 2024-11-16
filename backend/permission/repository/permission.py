from typing import Optional, Tuple, Union, List, Dict
from sqlalchemy import or_, select

from sqlalchemy.orm import joinedload

from config import logger
from core.repository.base_repository import BaseRepo, ModelType
from permission import Permission


class PermissionRepo(BaseRepo):
    def __init__(self) -> None:
        super(PermissionRepo, self).__init__(
            _model=Permission,
        )

    async def list(
            self,
            filters: Optional[Tuple] = (),
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sorts: Optional[List] = None,
            query_params_filters: Optional[Dict] = None
    ) -> List[ModelType]:
        try:
            statement = select(self._model).options(
                joinedload(self._model.menu),
                joinedload(self._model.user_group)
            ).where(*filters)
            result = await self._session.execute(statement)
            data = result.unique().scalars().all()
            return data
        except Exception as e:
            raise e

    async def get(self, filters: Optional[Tuple] = ()) -> Union[ModelType, None]:
        try:
            statement = select(self._model).options(
                joinedload(self._model.menu),
                joinedload(self._model.user_group)
            ).where(*filters)
            result = await self._session.execute(statement)
            data = result.scalars().first()
            return data
        except Exception as e:
            raise e

    async def get_permission_subquery_data(self, group_id_list):
        return await self.list(
            filters=(
                or_(
                    self._model.create == True,
                    self._model.edit == True,
                    self._model.view == True,
                    self._model.list == True,
                    self._model.delete == True
                ),
                self._model.group_id.in_(group_id_list),
                self._model.deleted_at == None
            )
        )

    async def get_permissions_sort_by_menu(self, filters: Optional[Tuple] = ()):
        try:
            statement = select(self._model).options(
                joinedload(self._model.menu),
                joinedload(self._model.user_group)
            ).where(*filters)
            statement = statement.order_by(self._model.menu_id.asc())
            result = await self._session.execute(statement)
            data = result.unique().scalars().all()
            return data
        except Exception as e:
            logger.error(f"{str(e)}")
