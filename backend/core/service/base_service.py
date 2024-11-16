import re
from abc import ABC
from datetime import datetime
from fastapi import HTTPException, status, Depends
from pydantic.main import BaseModel
from typing import Optional, Tuple, Dict
from core.utils import request_user


from sqlalchemy import desc, asc, text

from auth import User
from config import logger, Base
from core.const import FILTERTYPE
from typing import  Annotated, Any, Generic, TypeVar

from core.repository.base_repository import BaseRepo

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepo)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType], ABC):
    def __init__(
            self,
            repository: Annotated[RepositoryType, Depends()],
            read_schema: type[ReadSchemaType]
    ):
        self.repository = repository
        self.read_schema = read_schema
        self.filter_operations = {f"{FILTERTYPE.EXACT}": "__eq__", f"{FILTERTYPE.CONTAINS}": "contains"}
    async def get_db_obj(self, record_id: Any) -> ModelType:
        """
        get_db_obj

        Retrieves an entity from the SQLAlchemy model.

        Args:
        - record_id: The ID of the record to retrieve.

        Returns:
        - ModelType: The retrieved entity.

        Raises:
        - EntityNotFound: If the entity with the given ID is not found.

        """
        async with self.repository:
            db_obj = await self.repository.get(
                filters=(
                    self.repository._model.id == record_id,
                    self.repository._model.deleted_at == None
                )
            )
        if not db_obj:
            logger.info(f"{self.repository._model.__name__} with id: {record_id} data not found!")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{str(self.repository._model.__name__).title()} data not found!"
            )

        return db_obj

    """
        Insert 
    """

    async def insert(
            self,
            create_schema: CreateSchemaType,
            current_user: ModelType | None = None
    ):
        await self._validate(create_schema)
        return await self.__insert(create_schema.__dict__, current_user)

    async def _insert(
            self,
            create_data: dict,
            current_user: ModelType | None = None
    ):
        return await self.__insert(create_data, current_user)

    async def __insert(
            self,
            create_data: dict,
            current_user: ModelType | None = None
    ):
        async with self.repository:
            try:
                if current_user:
                    data = self._prepare_create(create_data, current_user)
                data = await self.repository.create(create_data)
            except Exception as e:
                logger.error(f"Could not insert {self.repository._model.__name__}, Reason: {e}")
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, detail=f"Could not insert {self.repository._model.__name__}")
        return self.read_schema(**data.__dict__)

    """
    Edit
    """

    async def   edit(
            self,
            record_id: int,
            update_schema: UpdateSchemaType,
            current_user: ModelType | None = None
    ) -> ReadSchemaType:

        await self._validate(update_schema, record_id)

        return await self.__edit(record_id, update_schema.__dict__, current_user)

    async def _edit(
            self,
            record_id: int,
            update_data: dict,
            current_user: ModelType | None = None
    ) -> ReadSchemaType:
        return await self.__edit(record_id, update_data, current_user)

    async def __edit(
            self,
            record_id: int,
            update_data: dict,
            current_user: ModelType | None = None
    ) -> ReadSchemaType:

        db_object = await self.get_db_obj(record_id=record_id)
        update_data = self._prepare_update(update_data, current_user)
        async with self.repository:
            try:
                if current_user:
                    data = await self.repository.update(
                        db_object,
                        update_data
                    )
            except Exception as e:
                logger.error(f"Could not update {self.repository._model.__name__}, Reason: {e}")
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, detail=f"Could not update {self.repository._model.__name__}")
        return self.read_schema(**data.__dict__)


    """
    Delete
    """

    async def delete(
            self,
            record_id: Any,
            current_user: ModelType | None = None
    ) -> None:
        """
        delete

        Deletes an entity from the repository.

        Args:
        - record_id: The ID of the record to delete.

        Raises:
        - EntityDeleteFailed: If the entity deletion fails.

        """

        db_obj =  await self.get_db_obj(record_id)
        async with self.repository:
            await self.repository.soft_delete(
                instance=[db_obj],
                current_user_id=current_user.id if current_user else None
            )
        logger.info(f"{self.repository._model.__name__} with id: {record_id} deleted successfully")


        """
            View
        """

    async def all(self, query: Dict = {}, filters: Optional[Dict[str, Any]] = {}):
        filters = self.prepare_manual_filters(filters)
        query_params_filters = self.prepare_filters(query) or {}
        sorts = self.prepare_sort(query) or []
        async with self.repository:
            data = await self.repository.list(
                filters=filters,
                query_params_filters=query_params_filters,
                sorts=sorts
            )
        return data

    async def filter(self, filters: dict = dict()):
        sorts =  []
        async with self.repository:
            data = await self.repository.list(
                manual_filters=(self.repository._model.deleted_at == None, ),
                filters=filters,
                sorts=sorts
            )
        return data

    async def get(self,  record_id: int) -> ReadSchemaType:
        data = await self.get_db_obj(record_id)
        return self.read_schema(**data.__dict__)

    def prepare_manual_filters(self, manual_filters: Dict):

        filters = (self.repository._model.deleted_at == None, )
        for key, value in manual_filters.items():
            operator = self.filter_operations.get(FILTERTYPE.EXACT, None)
            column = getattr(self.repository._model, key, None)
            if not column:
                logger.error(
                    f"Filter field name {key} not present in model {self.repository.model.__name__}")
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=f"Filter field name {key} not present in model {self.repository.model.__name__}"
                )
            filter_attr = getattr(column, operator)
            filter_query = filter_attr(value)
            filters = filters + (filter_query,)

        return filters

    def prepare_filter(self, field, operator, value):
        column = getattr(self.repository._model, field, None)
        if not column:
            logger.error(
                f"Filter field name {field} not present in model {self.repository.model.__name__}")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Filter field name {field} not present in model {self.repository.model.__name__}"
            )

        if not operator: operator = FILTERTYPE.EXACT
        operator = self.filter_operations.get(operator, None)
        if not operator:
            logger.error("Filter operator is not valid")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Filter operator is not valid")
        if value.isdigit():
            value = int(value)
        elif value.lower() == "true" or value.lower == 'false':
            if value.lower() == "true":
                value = True
            else:
                value = False
        elif value.lower() == "null":
            value = None
        else:
            if operator == FILTERTYPE.CONTAINS:
                value = "%{}%".format(value.strip())
            else:
                value = value

        return column, value, operator

    def prepare_filters(self, query: dict) -> dict:
        filters = dict()
        for key, value in query.items():
            if not key.startswith("filter"): continue
            # This extracts the filter field name and, filter type from query param
            match = re.search(r"filter\[(.*?)\](?:\[(.*?)\])?", key)
            if not match: continue
            field = match.group(1)
            operator = match.group(2)
            filter = self.prepare_filter(field, operator, value)
            # filter[0] = field instance, filter[1] = value, filter[2] = operator
            filters[filter[0]] = (filter[1], filter[2])

        return filters

    def prepare_sort(self, query) -> list:
        # Default sorting is bt ID in descending order
        sort = query.get("sort", "-id")
        sort_criteria = []
        for field in sort.split(','):
            if field.startswith("-"):
                field = field[1:]
                sort_criteria.append(desc(text(field)))
            else:
                sort_criteria.append(asc(text(field)))
            self.__valid_field(field)

        return sort_criteria

    def __valid_field(self, field: str):
        valid_field = getattr(self.repository._model, field, None)
        if not valid_field:
            logger.error(f"Field {field} is not a valid field of model {self.repository._model.__name__}")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Field {field} is not a valid field of model {self.repository._model.__name__}"
            )
        return valid_field

    async def _validate(self, data: CreateSchemaType | UpdateSchemaType, record_id: int | None = None):
        pass

    def _prepare_create(self, data, current_user: User):
        data['created_by_id'] = current_user.id
        return data

    def _prepare_update(self, data, current_user: User):
        data['updated_by_id'] = current_user.id
        data['updated_at'] = datetime.now()
        return data


