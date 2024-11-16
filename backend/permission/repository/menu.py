from typing import Optional, Tuple, List, Dict

from sqlalchemy import select

from config import logger
from core.repository.base_repository import BaseRepo
from permission import Menu
from sqlalchemy.orm import joinedload


class MenuRepo(BaseRepo):
    def __init__(self) -> None:
        super(MenuRepo, self).__init__(
            _model=Menu,
        )

    async def get_menus_sort_by_serial(self, filters: Optional[Tuple] = ()):
        try:
            statement = select(self._model).where(*filters)
            statement = statement.order_by(self._model.menu_serial.asc())
            result = await self._session.execute(statement)
            data = result.unique().scalars().all()
            return data
        except Exception as e:
            logger.error(f"{str(e)}")

    async def list(
            self,
            filters: Optional[Tuple] = (),
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sorts: Optional[List] = None,
            query_params_filters: Optional[Dict] = None,
    ) -> List[Menu]:
        try:
            statement = select(self._model).options(
                joinedload(self._model.module),
                joinedload(self._model.parent)
            ).where(*filters)
            if query_params_filters:
                statement = self.apply_filters(statement, query_params_filters)
            if sorts:
                statement = statement.order_by(*sorts)
            if limit is not None and offset is not None:
                statement = statement.offset(offset).limit(limit)
            result = await self._session.execute(statement)
            data = result.scalars().all()
            return data
        except Exception as e:
            logger.error(f"{str(e)}")
            raise e

    async def get(self, filters: Optional[Tuple] = ()) -> Menu:
        try:
            statement = select(self._model).options(
                joinedload(self._model.module),
                joinedload(self._model.parent)
            ).where(*filters)
            result = await self._session.execute(statement)
            data = result.scalars().first()
            return data
        except Exception as e:
            raise e