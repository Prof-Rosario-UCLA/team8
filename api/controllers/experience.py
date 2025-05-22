from ..models import db, User, Experience, BulletPoint, Skill, ParentType
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Optional, List
from uuid import UUID
from .bullet_point import serialize_bullet_point
from .skill import serialize_skill
from .utils import get_or_404, get_resolved_field
import datetime


def serialize_experience(
    experience_instance: Experience,
    field_overrides_dict: Optional[dict] = None,
    include_bullets_if_no_override: bool = False,
    include_skills_if_no_override: bool = False,
):
    """
    Serializes an Experience instance.
    If field_overrides_dict is provided, applies overrides and returns only resolved data fields.
    Otherwise, serializes global data and can include bullets/skills based on flags.
    """
    if not experience_instance:
        return None

    overrides = field_overrides_dict or {}
    is_resume_context = bool(field_overrides_dict)

    data = {
        "id": str(experience_instance.id),
        "user_id": str(experience_instance.user_id),
        "role": get_resolved_field(
            experience_instance, overrides, "role", experience_instance.role
        ),
        "company": get_resolved_field(
            experience_instance, overrides, "company", experience_instance.company
        ),
        "location": get_resolved_field(
            experience_instance, overrides, "location", experience_instance.location
        ),
        "desc_long": get_resolved_field(
            experience_instance, overrides, "desc_long", experience_instance.desc_long
        ),
    }

    raw_start_date = get_resolved_field(
        experience_instance, overrides, "start", experience_instance.start
    )
    if isinstance(raw_start_date, (datetime.date, datetime.datetime)):
        data["start"] = raw_start_date.isoformat()
    else:
        data["start"] = raw_start_date

    raw_end_date = get_resolved_field(
        experience_instance, overrides, "end", experience_instance.end
    )
    if isinstance(raw_end_date, (datetime.date, datetime.datetime)):
        data["end"] = raw_end_date.isoformat()
    else:
        data["end"] = raw_end_date

    if not is_resume_context:
        if include_bullets_if_no_override:
            data["bullets"] = [b.content for b in experience_instance.bullets]
        if include_skills_if_no_override:
            data["skills"] = [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "category": s.category.value if s.category else None,
                }
                for s in experience_instance.skills
            ]

    return data


# --- CRUD Functions for Experience ---


def create_experience(user_id, data):
    """Creates a new experience entry for a user."""
    user = User.query.get_or_404(user_id)
    try:
        experience = Experience(
            user_id=user.id,
            role=data.get("role"),
            company=data.get("company"),
            location=data.get("location"),
            start=data.get("start_date"),
            end=data.get("end_date"),
            desc_long=data.get("desc_long"),
        )
        db.session.add(experience)
        db.session.commit()  # Commit to get experience.id

        # Handle bullets
        if "bullets" in data and isinstance(data["bullets"], list):
            for idx, bullet_content in enumerate(data["bullets"]):
                bullet = BulletPoint(
                    parent_id=experience.id,
                    parent_type=ParentType.experience,
                    order_index=idx,
                    content=bullet_content,
                )
                db.session.add(bullet)

        # Handle skills (assuming data['skill_ids'] is a list of skill UUIDs)
        if "skill_ids" in data and isinstance(data["skill_ids"], list):
            for skill_id in data["skill_ids"]:
                skill = Skill.query.get(skill_id)
                if skill:
                    experience.skills.append(skill)

        db.session.commit()
        return serialize_experience(
            experience,
            include_bullets_if_no_override=True,
            include_skills_if_no_override=True,
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating experience: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for experience creation: {str(e)}")


def get_experience(experience_id, include_bullets=False, include_skills=False):
    """Retrieves a specific experience entry."""
    options = []
    if include_bullets:
        options.append(joinedload(Experience.bullets))
    if include_skills:
        options.append(joinedload(Experience.skills))

    experience = Experience.query.options(*options).get_or_404(experience_id)
    return serialize_experience(
        experience,
        include_bullets_if_no_override=include_bullets,
        include_skills_if_no_override=include_skills,
    )


def get_all_experiences_for_user(user_id, include_bullets=False, include_skills=False):
    """Retrieves all experience entries for a given user."""
    user = User.query.get_or_404(user_id)
    options = []
    if include_bullets:
        options.append(joinedload(Experience.bullets))
    if include_skills:
        options.append(joinedload(Experience.skills))

    experiences = Experience.query.options(*options).filter_by(user_id=user_id).all()
    return [
        serialize_experience(
            exp,
            include_bullets_if_no_override=include_bullets,
            include_skills_if_no_override=include_skills,
        )
        for exp in experiences
    ]


def update_experience(experience_id, data):
    """Updates an existing experience entry."""
    experience = Experience.query.options(
        joinedload(Experience.bullets), joinedload(Experience.skills)
    ).get_or_404(experience_id)
    try:
        if "role" in data:
            experience.role = data["role"]
        if "company" in data:
            experience.company = data["company"]
        if "location" in data:
            experience.location = data["location"]
        if "start_date" in data:
            experience.start = data["start_date"]
        if "end_date" in data:
            experience.end = data["end_date"]
        if "desc_long" in data:
            experience.desc_long = data["desc_long"]

        if "bullets" in data and isinstance(data["bullets"], list):
            BulletPoint.query.filter_by(
                parent_id=experience.id, parent_type=ParentType.experience
            ).delete()
            for idx, bullet_content in enumerate(data["bullets"]):
                db.session.add(
                    BulletPoint(
                        parent_id=experience.id,
                        parent_type=ParentType.experience,
                        order_index=idx,
                        content=bullet_content,
                    )
                )

        if "skill_ids" in data and isinstance(data["skill_ids"], list):
            experience.skills.clear()  # Remove existing skills
            for skill_id in data["skill_ids"]:
                skill = Skill.query.get(skill_id)
                if skill:
                    experience.skills.append(skill)

        db.session.commit()
        updated_experience = Experience.query.options(
            joinedload(Experience.bullets), joinedload(Experience.skills)
        ).get(experience_id)
        return serialize_experience(
            updated_experience,
            include_bullets_if_no_override=True,
            include_skills_if_no_override=True,
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating experience: {str(e)}")


def delete_experience(experience_id):
    """Deletes an experience entry."""
    experience = Experience.query.get_or_404(experience_id)
    try:
        db.session.delete(experience)  # Bullets and skill associations should cascade
        db.session.commit()
        return {"message": "Experience entry deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting experience: {str(e)}")


# --- Skill Association for Experience ---
def add_skill_to_experience(experience_id, skill_id):
    experience = Experience.query.get_or_404(experience_id)
    skill = Skill.query.get_or_404(skill_id)
    try:
        if skill not in experience.skills:
            experience.skills.append(skill)
            db.session.commit()
        return serialize_experience(experience, include_skills_if_no_override=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error adding skill to experience: {str(e)}")


def remove_skill_from_experience(experience_id, skill_id):
    experience = Experience.query.get_or_404(experience_id)
    skill = Skill.query.get_or_404(skill_id)
    try:
        if skill in experience.skills:
            experience.skills.remove(skill)
            db.session.commit()
        return serialize_experience(experience, include_skills_if_no_override=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing skill from experience: {str(e)}")
