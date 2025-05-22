import enum, uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    Boolean,
    create_engine,
    Enum,
    func,
    event,
    literal,
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
