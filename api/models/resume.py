import enum
from datetime import datetime

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
    resume_name: Mapped[str | None] = mapped_column(nullable=False)
    template_id = mapped_column(ForeignKey(Template.id), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sections: Mapped[List["ResumeSection"]] = relationship(
        back_populates="resume",
        order_by="ResumeSection.display_order",
        cascade="all, delete-orphan",
    )

    user: Mapped["User"] = relationship(back_populates="resumes")

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "template_id": self.template_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "name": self.user.name,
            "resume_name": self.resume_name or "Untitled Resume",
            "phone": self.user.phone,
            "email": self.user.email,
            "linkedin": self.user.linkedin,
            "github": self.user.github,
            "website": self.user.website,
            "sections": [sec.json() for sec in self.sections],
        }


class ResumeItemType(enum.Enum):
    education = "education"
    experience = "experience"
    project = "project"
    skill = "skill"


SECTION_TYPE_TO_DISPLAY_NAME_MAPPING = {
    ResumeItemType.education: "Education",
    ResumeItemType.experience: "Experience",
    ResumeItemType.project: "Project",
    ResumeItemType.skill: "Technical Skills",
}


class ResumeSection(db.Model, Base):
    __tablename__ = "resume_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    resume_id: Mapped[int] = mapped_column(ForeignKey(Resume.id), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    section_type: Mapped[ResumeItemType] = mapped_column(nullable=False)
    display_order: Mapped[int] = mapped_column(default=0)

    resume: Mapped[Resume] = relationship(back_populates="sections")
    items: Mapped[List["ResumeItem"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="ResumeItem.display_order",
    )

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "resume_id": self.resume_id,
            "name": self.name,
            "section_type": self.section_type.value,
            "display_order": self.display_order,
            "items": [item.json() for item in self.items],
        }


class ResumeItem(db.Model, Base):
    __tablename__ = "resume_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))

    # university degree, job title, project name
    title: Mapped[str] = mapped_column(nullable=False)
    # university, company, (optional) project group
    organization: Mapped[str] = mapped_column(nullable=False)
    # start date
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # end date
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # university location, job location, GitHub project URL
    location: Mapped[str] = mapped_column(nullable=False)
    # Bulletpoints not saved but bullet items are on each line
    description: Mapped[str] = mapped_column(nullable=False)

    section_id: Mapped[int] = mapped_column(
        ForeignKey("resume_sections.id", ondelete="CASCADE")
    )
    display_order: Mapped[int] = mapped_column(default=0)

    section: Mapped["ResumeSection"] = relationship(back_populates="items")

    @override
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "section_id": self.section_id,  # Include parent section ID
            "title": self.title,
            "organization": self.organization,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "location": self.location,
            "description": self.description,
            "display_order": self.display_order,
        }


# Associates a resume item with a resume section (many to many)
# class ResumeAssociation(db.Model, Base):
#     __tablename__ = "resume_associations"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
#     section_id: Mapped[int] = mapped_column(
#         ForeignKey("resume_sections.id", ondelete="CASCADE"), nullable=False
#     )
#     item_id: Mapped[int] = mapped_column(
#         ForeignKey("resume_items.id", ondelete="CASCADE"), nullable=False
#     )
#     display_order: Mapped[int] = mapped_column(default=0)

#     @override
#     def json(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "section_id": self.section_id,
#             "item_id": self.item_id,
#             "display_order": self.display_order,
#         }
