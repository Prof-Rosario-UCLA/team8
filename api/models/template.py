import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    String,
)

Base = declarative_base()


class Template(Base):
    __tablename__ = "templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    uri = Column(String, nullable=False)  # GCS link to LaTeX template
