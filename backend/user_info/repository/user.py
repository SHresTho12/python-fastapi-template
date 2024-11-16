from auth.model import User
from core.repository.base_repository import BaseRepo


from typing import Optional, Tuple, List, Dict

from sqlalchemy import select

from config import logger
from core.repository.base_repository import BaseRepo
from permission import Menu
from sqlalchemy.orm import joinedload


class UserRepo(BaseRepo):
    def __init__(self) -> None:
        super().__init__(
            _model=User,
        )

    async def list(
            self,
            manual_filters: Optional[Tuple] = (),
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            sorts: Optional[List] = None,
            filters: Optional[Dict] = None,
    ) -> List[Menu]:
        try:
            statement = select(self._model).options(
                joinedload(self._model.groups)
            ).where(*manual_filters)
            if filters:
                statement = self.apply_filters(statement, filters)
            if sorts:
                statement = statement.order_by(*sorts)
            if limit is not None and offset is not None:
                statement = statement.offset(offset).limit(limit)
            result = await self._session.execute(statement)
            data = result.unique().scalars().all()
            return data
        except Exception as e:
            logger.error(f"{str(e)}")

    async def get(self, filters: Optional[Tuple] = ()) -> Menu:
        try:
            statement = select(self._model).options(
                joinedload(self._model.groups),
            ).where(*filters)
            result = await self._session.execute(statement)
            data = result.scalars().first()
            return data
        except Exception as e:
            raise e