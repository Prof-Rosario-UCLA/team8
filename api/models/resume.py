import enum, uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy import Column, DateTime, String, ForeignKey, func

Base = declarative_base()


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    template_id = Column(ForeignKey("templates.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    education = Column(ARRAY(ForeignKey("resume_items.id")))
    experience = Column(ARRAY(ForeignKey("resume_items.id")))
    projects = Column(ARRAY(ForeignKey("resume_items.id")))
    blob = Column(JSONB())


class ResumeItemType(enum.Enum):
    experience = "experience"
    project = "project"
    education = "education"
    publication = "publication"
    award = "award"


class ResumeItem(Base):
    __tablename__ = "resume_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(ForeignKey("resumes.id"))
    item_type = Column(ResumeItemType, nullable=False)
    data = Column(String)
