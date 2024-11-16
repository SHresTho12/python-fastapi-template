import uuid

from sqlalchemy import Column, String, Integer, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from config import Base
from core.model_base import DependentCommonBase

user_type = Table(
    'user_type',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('type_id', Integer, ForeignKey('groups.id'))
)


class User(Base, DependentCommonBase):
    email = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=True)
    phone = Column(String)
    meta = Column(JSON, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)

    # relationships
    user_informations = relationship('UserInformation', foreign_keys="UserInformation.user_id", back_populates='user')

    groups = relationship(
        'Group',
        secondary=user_type,
        back_populates='users'
    )
    websites = relationship(
        "Website",
        back_populates="user",
        foreign_keys="Website.user_id"
    )

    @property
    def version_renew(self):
        try:
            meta = dict(self.meta)
        except:
            meta = {}
        meta['version'] = uuid.uuid4().hex
        return meta

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
