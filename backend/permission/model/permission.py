from sqlalchemy import Boolean, Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from config import Base
from core.const import DEFAULT_ACTION
from core.enums import PermissionType
from core.model_base import DependentCommonBase


class Permission(Base, DependentCommonBase):
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=False)
    action = Column(JSON, default=DEFAULT_ACTION)
    permission_type = Column(Integer, nullable=False, default=PermissionType.SELF_DATA.value)

    # relationships

    user_group = relationship("Group", back_populates="permissions")
    menu = relationship("Menu", back_populates="permissions")
