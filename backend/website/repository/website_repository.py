from core.repository.base_repository import BaseRepo
from website.model.website import Website

class WebsiteRepository(BaseRepo):
    def __init__(self) -> None:
        super().__init__(
            _model=Website,
        )




