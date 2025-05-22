from flask_sqlalchemy import SQLAlchemy

from .models import (
    Base,
    Website,
    ParentType,
    BulletPoint,
    Education,
    Experience,
    Project,
    Skill,
    SkillCategory,
    Template,
    Resume,
    ResumeSection,
    ResumeItem,
    ResumeBullet,
)

db = SQLAlchemy(model_class=Base)
