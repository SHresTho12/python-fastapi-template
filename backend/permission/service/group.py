from fastapi import HTTPException, status

from core.service.base_service import BaseService
from permission.repository.group import GroupRepo
from permission.schema.group import GroupView


class GroupService(BaseService):
    def __init__(self):
        self.repository = GroupRepo()
        self.read_schema = GroupView
        super().__init__(
            repository=self.repository,
            read_schema=self.read_schema
        )

    async def _validate(self, data, record_id: int | None = None):
        data = data.__dict__
        filters = (
            self.repository._model.name == data['name'],
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