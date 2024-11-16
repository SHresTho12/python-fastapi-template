from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from config import Base
from core.model_base import DependentCommonBase


class Module(Base, DependentCommonBase):
    name = Column(String, nullable=False)

    menus = relationship("Menu", back_populates="module")
