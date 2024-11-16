from sqlalchemy import Column, Integer, Float, ForeignKey, String, Date
from sqlalchemy.orm import relationship

from config import Base
from core.model_base import DependentCommonBase


class UserInformation(Base, DependentCommonBase):
    address = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    contact_information = Column(String)
    personal_information = Column(String)
    profile_picture = Column(String)
    date_of_birth = Column(Date)
    gender = Column(Integer)
    # relationships
    user = relationship(
        'User', foreign_keys=[user_id], back_populates='user_informations'
    )
