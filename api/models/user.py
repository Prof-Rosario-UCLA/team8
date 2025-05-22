import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    Integer,
    String,
)

from flask_login import UserMixin

Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_picture = Column(String, nullable=False)
