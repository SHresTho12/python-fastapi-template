import abc
from typing import Optional


class AbcRepository(abc.ABC):

    @abc.abstractmethod
    def get(self, query: dict):
        pass

    @abc.abstractmethod
    def list(self, query: dict, limit: Optional[int] = None):
        pass

    @abc.abstractmethod
    def create(self, data: dict):
        pass

    @abc.abstractmethod
    def update(self, query: dict, data: dict):
        pass

    @abc.abstractmethod
    def hard_delete(self, query: dict):
        pass

    @abc.abstractmethod
    def soft_delete(self, query: dict):
        pass