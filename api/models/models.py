"""
SQLAlchemy schema (PostgreSQL) for
• strict LaTeX-template rendering
• "reference + overlay" resume editing

All resume-specific mutations live in ResumeItem / ResumeBullet rows.
Global tables remain single source-of-truth for retrieval & future LLM workflows.
"""

import enum, uuid
from datetime import date
from sqlalchemy import (
    Table, Column, ForeignKey, ForeignKeyConstraint, Index,
    Date, DateTime, Integer, Numeric, String, Text, Boolean, create_engine,
    Enum, func, event, literal
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import DDL

Base = declarative_base()

# ------------------------------------------------------------------ #
#  User & ancillary
# ------------------------------------------------------------------ #

class User(Base):
    __tablename__ = "users"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = Column(String, nullable=False)
    email      = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    websites    = relationship("Website",  cascade="all, delete-orphan")
    educations  = relationship("Education", cascade="all, delete-orphan")
    experiences = relationship("Experience", cascade="all, delete-orphan")
    projects    = relationship("Project",   cascade="all, delete-orphan")
    resumes     = relationship("Resume",    cascade="all, delete-orphan")


class Website(Base):
    __tablename__ = "websites"
    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    alt     = Column(String)
    url     = Column(String, nullable=False)


# ------------------------------------------------------------------ #
#  Shared bullet-point store  (parent integrity via trigger)
# ------------------------------------------------------------------ #

class ParentType(enum.Enum):
    education   = "education"
    experience  = "experience"
    project     = "project"
    publication = "publication"
    award       = "award"

class BulletPoint(Base):
    __tablename__ = "bullet_points"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_type = Column(Enum(ParentType, name="bullet_parent_type"), nullable=False)
    parent_id   = Column(UUID(as_uuid=True), nullable=False)
    order_index = Column(Integer, nullable=False)
    content     = Column(Text, nullable=False)

    __table_args__ = (
        Index("idx_bp_parent", "parent_type", "parent_id"),
        Index("idx_bp_parent_order", "parent_type", "parent_id", "order_index", unique=True),
    )

# trigger ensures parent exists (PostgreSQL)
bp_trigger_sql = DDL("""
CREATE OR REPLACE FUNCTION bullet_parent_check() RETURNS trigger AS $$
BEGIN
  PERFORM 1 FROM
     CASE NEW.parent_type
       WHEN 'education'   THEN educations
       WHEN 'experience'  THEN experiences
       WHEN 'project'     THEN projects
       WHEN 'publication' THEN publications
       WHEN 'award'       THEN awards
     END
  WHERE id = NEW.parent_id;

  IF NOT FOUND THEN
    RAISE FOREIGN_KEY_VIOLATION USING MESSAGE = 'Invalid bullet parent';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS bullet_fk_check ON bullet_points;
CREATE CONSTRAINT TRIGGER bullet_fk_check
AFTER INSERT OR UPDATE ON bullet_points
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION bullet_parent_check();
""")
event.listen(BulletPoint.__table__, "after_create", bp_trigger_sql)


# ------------------------------------------------------------------ #
#  Core profile entities  (Education / Experience / Project)
# ------------------------------------------------------------------ #

def bullet_rel(cls, parent_type_literal):
    from sqlalchemy import and_
    return relationship(
        "BulletPoint",
        primaryjoin=lambda: and_(
            BulletPoint.parent_id == cls.id,
            BulletPoint.parent_type == literal(parent_type_literal)
        ),
        order_by=BulletPoint.order_index,
        cascade="all, delete-orphan"
    )

class Education(Base):
    __tablename__ = "educations"
    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id   = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    school    = Column(String, nullable=False)
    start     = Column(Date)
    end       = Column(Date)
    gpa       = Column(Numeric(3, 2))
    bullets   = bullet_rel(__qualname__, ParentType.education.value)
    desc_long = Column(Text)

class Experience(Base):
    __tablename__ = "experiences"
    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id   = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role      = Column(String)
    company   = Column(String)
    location  = Column(String)
    start     = Column(Date)
    end       = Column(Date)
    desc_long = Column(Text)

    bullets = bullet_rel(__qualname__, ParentType.experience.value)
    skills  = relationship("Skill", secondary=lambda: experience_skills)

class Project(Base):
    __tablename__ = "projects"
    id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id   = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title     = Column(String)
    role      = Column(String)
    start     = Column(Date)
    end       = Column(Date)
    desc_long = Column(Text)

    bullets = bullet_rel(__qualname__, ParentType.project.value)
    skills  = relationship("Skill", secondary=lambda: project_skills)

# ------------------------------------------------------------------ #
#  Skills + join tables
# ------------------------------------------------------------------ #

class SkillCategory(enum.Enum):
    language   = "language"
    framework  = "framework"
    library    = "library"
    cloud      = "cloud"
    tool       = "tool"

class Skill(Base):
    __tablename__ = "skills"
    id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name     = Column(String, nullable=False)
    category = Column(Enum(SkillCategory, name="skill_category"))

experience_skills = Table(
    "experience_skills", Base.metadata,
    Column("experience_id", ForeignKey("experiences.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id",      ForeignKey("skills.id",       ondelete="CASCADE"), primary_key=True)
)

project_skills = Table(
    "project_skills", Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id",   ForeignKey("skills.id",    ondelete="CASCADE"), primary_key=True)
)

# ------------------------------------------------------------------ #
#  Templates & resumes
# ------------------------------------------------------------------ #

class Template(Base):
    __tablename__ = "templates"
    id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    uri  = Column(String, nullable=False)   # GCS link to LaTeX template

class Resume(Base):
    __tablename__ = "resumes"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title       = Column(String)
    template_id = Column(ForeignKey("templates.id"))
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    template = relationship("Template")
    sections = relationship("ResumeSection", order_by="ResumeSection.order_index", cascade="all, delete-orphan")
    items    = relationship("ResumeItem",    cascade="all, delete-orphan")

class ResumeSection(Base):
    """
    Draggable top-level section order (projects, experience, etc.).
    """
    __tablename__ = "resume_sections"
    resume_id    = Column(ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True)
    section_type = Column(String, primary_key=True)   # 'projects', 'experience', etc.
    order_index  = Column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_resume_section_order", "resume_id", "order_index"),
    )

# ------------------------------------------------------------------ #
#  Overlay layer: per-resume items + bullet overrides
# ------------------------------------------------------------------ #

class ResumeItemType(enum.Enum):
    experience = "experience"
    project    = "project"
    education  = "education"
    publication= "publication"
    award      = "award"

class ResumeItem(Base):
    """
    Indicates that a global item is included in a resume, with optional
    per-resume text overrides (small diff, avoids duplication).
    """
    __tablename__ = "resume_items"
    resume_id   = Column(ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True)
    item_type   = Column(Enum(ResumeItemType, name="resume_item_type"), primary_key=True) # binds to a section of the resume
    item_id     = Column(UUID(as_uuid=True), primary_key=True)
    order_index = Column(Integer, nullable=False)

    # field_overrides will store a JSON object with keys like "title", "role", "description", "start_date", "end_date", etc.
    field_overrides = Column(JSONB, nullable=True) # Replaces custom_desc and allows for more field overrides

    # Relationship to overridden bullets (existing)
    # bullets = relationship("ResumeBullet", cascade="all, delete-orphan") # This relationship is implicitly handled by FKs on ResumeBullet

    # Relationship to overridden skills (new)
    overridden_skills = relationship("Skill", secondary=lambda: resume_item_skills, backref="resume_items")

    __table_args__ = (
        Index("idx_resume_items_order", "resume_id", "order_index"),
    )

# New association table for resume-specific skill overrides
resume_item_skills = Table(
    "resume_item_skills", Base.metadata,
    Column("resume_id", UUID(as_uuid=True), nullable=False),
    Column("item_type", Enum(ResumeItemType, name="resume_item_skill_item_type"), nullable=False), # Name must be unique for Enum type in DB
    Column("item_id", UUID(as_uuid=True), nullable=False),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True), # skill_id is part of PK
    ForeignKeyConstraint(
        ["resume_id", "item_type", "item_id"],
        ["resume_items.resume_id", "resume_items.item_type", "resume_items.item_id"],
        ondelete="CASCADE"
    ),
    PrimaryKeyConstraint("resume_id", "item_type", "item_id", "skill_id") # Composite primary key
)

class ResumeBullet(Base):
    """
    Overrides global bullets for a given ResumeItem.  
    Rows exist **only** when user edits within resume; otherwise global bullets
    are rendered.
    """
    __tablename__ = "resume_bullets"
    resume_id   = Column(UUID(as_uuid=True), primary_key=True)
    item_type   = Column(Enum(ResumeItemType, name="resume_bullet_item_type"), primary_key=True)
    item_id     = Column(UUID(as_uuid=True), primary_key=True)
    order_index = Column(Integer, primary_key=True)
    content     = Column(Text, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["resume_id", "item_type", "item_id"],
            ["resume_items.resume_id", "resume_items.item_type", "resume_items.item_id"],
            ondelete="CASCADE"
        ),
    )