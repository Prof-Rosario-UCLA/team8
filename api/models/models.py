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
    Table, Column, ForeignKey, ForeignKeyConstraint, Index, PrimaryKeyConstraint,
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
    bullets   = relationship("BulletPoint",
                            primaryjoin="and_(BulletPoint.parent_id==Education.id, BulletPoint.parent_type=='education')",
                            cascade="all, delete-orphan",
                            order_by="BulletPoint.order_index")
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

    bullets = relationship("BulletPoint",
                            primaryjoin="and_(BulletPoint.parent_id==Experience.id, BulletPoint.parent_type=='experience')",
                            cascade="all, delete-orphan",
                            order_by="BulletPoint.order_index")
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

    bullets = relationship("BulletPoint",
                            primaryjoin="and_(BulletPoint.parent_id==Project.id, BulletPoint.parent_type=='project')",
                            cascade="all, delete-orphan",
                            order_by="BulletPoint.order_index")
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
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    template = relationship("Template")
    sections = relationship("ResumeSection", cascade="all, delete-orphan", order_by="ResumeSection.order_index")
    items    = relationship("ResumeItem",    cascade="all, delete-orphan", order_by="ResumeItem.order_index")

# ------------------------------------------------------------------ #
#  Overlay layer: per-resume items + bullet overrides
# ------------------------------------------------------------------ #

class ResumeItemType(enum.Enum):
    experience = "experience"
    project    = "project"
    education  = "education"
    publication= "publication"
    award      = "award"

class ResumeSection(Base):
    """
    Represents a typed section within a resume (e.g., "Experience", "Projects").
    The order of these types is managed by order_index.
    The title is customizable by the user (e.g., "Work History" for an "experience" type section).
    """
    __tablename__ = "resume_sections"
    resume_id    = Column(ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True)
    section_type = Column(Enum(ResumeItemType, name="rs_section_item_type"), primary_key=True) # e.g., experience, project
    title        = Column(String, nullable=False) # User-defined title, e.g., "Work Experience"
    order_index  = Column(Integer, nullable=False) # Defines the order of section types

    items = relationship(
        "ResumeItem",
        primaryjoin="and_(ResumeItem.resume_id==ResumeSection.resume_id, ResumeItem.item_type==ResumeSection.section_type)",
        cascade="all, delete-orphan",
        order_by="ResumeItem.order_index" 
    )

    __table_args__ = (
        Index("idx_resume_section_order", "resume_id", "order_index", unique=True), # Order index should be unique per resume
    )

class ResumeItem(Base):
    """
    Indicates that a global item is included in a resume, with optional
    per-resume text overrides (small diff, avoids duplication).
    """
    __tablename__ = "resume_items"
    resume_id   = Column(ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True)
    item_type   = Column(Enum(ResumeItemType, name="ri_item_type"), primary_key=True) 
    item_id     = Column(UUID(as_uuid=True), primary_key=True) # ID of the global item (Education, Experience, etc.)
    order_index = Column(Integer, nullable=False) # Order within its section

    # field_overrides will store a JSON object with keys like "title", "role", "description", "start_date", "end_date", etc.
    field_overrides = Column(JSONB, nullable=True) # Replaces custom_desc and allows for more field overrides

    # Relationship to overridden bullets 
    bullets = relationship("ResumeBullet", cascade="all, delete-orphan", order_by="ResumeBullet.order_index")

    # Relationship to overridden skills 
    overridden_skills = relationship("Skill", secondary=lambda: resume_item_skills, backref="resume_items")

    __table_args__ = (
        # Foreign key to ResumeSection
        ForeignKeyConstraint(
            ["resume_id", "item_type"],
            ["resume_sections.resume_id", "resume_sections.section_type"],
            ondelete="CASCADE"
        ),
        Index("idx_resume_items_order_in_section", "resume_id", "item_type", "order_index", unique=True),
    )

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