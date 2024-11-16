from core.repository.base_repository import BaseRepo
from user_info import UserInformation


class UserInformationRepo(BaseRepo):
    def __init__(self) -> None:
        super().__init__(
            _model=UserInformation,
        )
