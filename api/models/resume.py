import enum

from typing import List, override

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from models.user import User
from models.template import Template


from db import db


class Resume(db.Model, Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(nullable=False)
    template_id = mapped_column(ForeignKey(Template.id), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sections: Mapped[List["ResumeSection"]] = relationship(back_populates="resume")

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "name": self.name,
            "sections": [sec.json() for sec in self.sections],
        }


class ResumeItemType(enum.Enum):
    education = "education"
    experience = "experience"
    project = "project"
    skill = "skill"


class ResumeSection(db.Model, Base):
    __tablename__ = "resume_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    resume_id: Mapped[int] = mapped_column(ForeignKey(Resume.id), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    section_type: Mapped[ResumeItemType] = mapped_column(nullable=False)

    resume: Mapped[Resume] = relationship(back_populates="sections")

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "resume_id": self.resume_id,
            "name": self.name,
            "section_type": self.section_type,
        }


class ResumeItem(db.Model, Base):
    __tablename__ = "resume_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    item_type: Mapped[ResumeItemType] = mapped_column(nullable=False)

    # university degree, job title, project name
    title: Mapped[str] = mapped_column(nullable=False)
    # university, company, (optional) project group
    organization: Mapped[str] = mapped_column(nullable=False)
    # start date
    start_date: Mapped[str] = mapped_column(nullable=False)
    # end date
    end_date: Mapped[str]
    # university location, job location, GitHub project URL
    location: Mapped[str] = mapped_column(nullable=False)
    # Bulletpoints not saved but bullet items are on each line
    description: Mapped[str] = mapped_column(nullable=False)

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_type": self.item_type,
            "title": self.title,
            "organization": self.organization,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "location": self.location,
            "description": self.description,
        }


# Associates a resume item with a resume section (many to many)
class ResumeAssociation(db.Model, Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    section: Mapped[ResumeSection] = mapped_column(
        ForeignKey(ResumeSection.id, ondelete="CASCADE"), nullable=False
    )
    item: Mapped[ResumeItem] = mapped_column(
        ForeignKey(ResumeItem.id, ondelete="CASCADE"), nullable=False
    )

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "section": self.section.id,
            "item": self.item.id,
        }
