from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from config import Base
from core.enums import MenuType
from core.model_base import DependentCommonBase


class Menu(Base, DependentCommonBase):
    name = Column(String(255), nullable=True)
    module_id = Column(Integer, ForeignKey('modules.id'))
    menu_type = Column(Integer, nullable=True, default=MenuType.PARENT.value)
    parent_menu = Column(Integer, ForeignKey('menus.id'))
    menu_serial = Column(Integer, nullable=True)
    api_end_point = Column(String(255), nullable=True)
    menu_icon = Column(String(255), nullable=True)
    menu_url = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    # relationships
    parent = relationship("Menu",remote_side='Menu.id', foreign_keys=[parent_menu])
    module = relationship("Module", foreign_keys=[module_id], back_populates='menus')
    permissions = relationship("Permission", back_populates="menu")
