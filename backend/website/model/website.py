from  sqlalchemy import (
    Column,
    Boolean,
    String,
    JSON,
    Integer,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship

from config import Base
from core.enums import Tools
from core.model_base import DependentCommonBase

class Website(Base, DependentCommonBase):
    __tablename__ = "websites"

    name = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    #relationship
    user = relationship(
        "User",
        back_populates="websites",
        foreign_keys=[user_id]
    )
    website_settings = relationship(
        "WebsiteSettings",
        back_populates="website"
    )


class WebsiteSettings(Base,DependentCommonBase):
    __tablename__ = 'website_settings'

    name = Column(String)
    website_id = Column(Integer,ForeignKey("websites.id"))
    settings_data =  Column(JSON)
    tools = Column(String, nullable=True)

    #relationship
    website = relationship(
        "Website",
        back_populates = "website_settings"
    )