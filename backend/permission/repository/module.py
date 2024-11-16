from core.repository.base_repository import BaseRepo

from permission import Module


class ModuleRepo(BaseRepo):
    def __init__(self) -> None:
        super(ModuleRepo, self).__init__(
            _model=Module,
        )
