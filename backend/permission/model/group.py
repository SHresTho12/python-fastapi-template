from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from auth import user_type
from config import Base
from core.model_base import DependentCommonBase


class Group(Base, DependentCommonBase):
    name = Column(String, nullable=True)
    is_protected = Column(Boolean, default=False)

    permissions = relationship("Permission", back_populates="user_group", lazy='dynamic')

    users = relationship(
        'User',
        secondary=user_type,
        back_populates='groups'
    )
