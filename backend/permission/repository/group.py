from core.repository.base_repository import BaseRepo


class GroupRepo(BaseRepo):
    def __init__(self) -> None:
        from permission.model.group import Group
        super(GroupRepo, self).__init__(
            _model=Group,
        )
