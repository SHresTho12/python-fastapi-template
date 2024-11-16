from datetime import datetime
from typing import TypeVar, Optional, Tuple, Union, List, Dict

from fastapi import HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete, func
from sqlalchemy.util._collections import immutabledict

from config import get_session, logger, Base
from core.repository.abc_repository import AbcRepository
from core.enums import Status

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepo(AbcRepository):
    def __init__(self, _model: ModelType) -> None:
        super().__init__()
        self._model = _model
        self._session = None

    async def __aenter__(self):
        async with get_session() as session:
            self._session = session

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._session:
            await self._session.__aexit__(exc_type, exc_value, traceback)

    async def get(self, filters: Optional[Tuple] = ()) -> Union[ModelType, None]:
        try:
            statement = select(self._model).where(*filters)
            result = await self._session.execute(statement)
            data = result.scalars().first()
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
    ) -> List[ModelType]:
        try:
            statement = select(self._model).where(*filters)
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

    async def count(
            self, filters: Optional[Tuple] = ()
    ) -> List[ModelType]:
        try:
            statement = select(func.count()).select_from(self._model).where(*filters)
            result = await self._session.execute(statement)
            data = result.scalars().first()
            return data
        except Exception as e:
            logger.error(f"{str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )

    async def create(self, data: dict) -> ModelType:
        try:
            instance = self._model(**data)
            self._session.add(instance)
            await self._session.commit()
            await self._session.refresh(instance)
            return instance
        except Exception as e:
            await self._session.rollback()
            logger.error(f"{str(e)}")
            raise e

    async def update(
            self,
            instance: ModelType,
            update_data: dict,
            is_add: bool = True,
            is_commit: bool = True
    ):
        try:
            _instance = jsonable_encoder(instance)
            for field in _instance:
                if field in update_data and update_data.get(field, None) is not None:
                    setattr(instance, field, update_data.get(field, None))
            if is_add:
                self._session.add(instance)
            if is_commit:
                await self._session.commit()
            return instance
        except Exception as e:
            await self._session.rollback()
            logger.error(f"{str(e)}")
            raise e

    async def hard_delete(self, filters: Optional[Tuple] = ()):
        try:
            statement = delete(self._model).where(*filters)
            await self._session.execute(statement, execution_options=immutabledict({"synchronize_session": 'fetch'}))
            await self._session.commit()
        except Exception as e:
            await self._session.rollback()
            logger.error(f"{str(e)}")
            raise e

    async def soft_delete(self, instance: List[ModelType], current_user_id: int = None):
        try:
            for data in instance:
                data.deleted_at = datetime.now()
                data.deleted_by_id = current_user_id
                data.status = Status.DELETE.value
            self._session.add_all(instance)
            await self._session.commit()
        except Exception as e:
            logger.error(f"{str(e)}")

    # async def __aexit__(self, exc_type, exc_value, traceback):
    #             await self._session.close()

    def apply_filters(self, query, filters) -> Query:
        if not filters: return query
        for key, value in filters.items():
            field_value = value[0]
            filter_operation = value[1]
            filter_attr = getattr(key, filter_operation)
            query = query.where(filter_attr(field_value))

        return query
