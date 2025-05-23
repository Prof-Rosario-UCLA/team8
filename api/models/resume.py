import enum

from typing import List

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.user import User


from db import db

class Resume(db.Model):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(nullable=False)
    # template_id = Column(ForeignKey("templates.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    education: Mapped[List["ResumeItem"]] = relationship(back_populates="resume")
    # education = Column(ARRAY(ForeignKey("resume_items.id")))
    # experience = Column(ARRAY(ForeignKey("resume_items.id")))
    # projects = Column(ARRAY(ForeignKey("resume_items.id")))
    # blob = Column(JSONB())

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'education': [edu.json() for edu in self.education]
        }

class ResumeItemType(enum.Enum):
    experience = "experience"
    project = "project"
    education = "education"
    publication = "publication"
    award = "award"

class ResumeItem(db.Model):
    __tablename__ = "resume_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey(Resume.id), nullable=False)
    resume: Mapped[Resume] = relationship(back_populates="education")
    item_type: Mapped[ResumeItemType] = mapped_column(nullable=False)

    def json(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'item_type': self.item_type
        }
