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
    name: Mapped[str] = mapped_column(nullable=False)
    template_id = mapped_column(ForeignKey("templates.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sections: Mapped[List["ResumeSection"]] = relationship(back_populates="resume")

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "name": self.name,
            "sections": [sec.json() for sec in self.sections],
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class ResumeSection(db.Model):
    __tablename__ = "resume_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey(Resume.id), nullable=False)

    resume: Mapped[Resume] = relationship(back_populates="sections")
    items: Mapped[List["ResumeItem"]] = relationship(back_populates="section")

    def json(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "items": [item.json() for item in self.items],
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class ResumeItemType(enum.Enum):
    education = "education"
    experience = "experience"
    project = "project"
    skill = "skill"


class ResumeItem(db.Model):
    __tablename__ = "resume_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(
        ForeignKey(ResumeSection.id), nullable=False
    )
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

    section: Mapped[Resume] = relationship(back_populates="items")

    def json(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "item_type": self.item_type,
            "title": self.title,
            "organization": self.organization,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "location": self.location,
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
