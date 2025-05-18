from ..models import db, User, Experience, BulletPoint, Skill, ParentType
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Optional, List
from uuid import UUID
from .bullet_point_controller import serialize_bullet_point
from .skill_controller import serialize_skill
from .utils import get_or_404, get_resolved_field
import datetime

def serialize_experience_detail(
    experience_instance: Experience,
    field_overrides_dict: Optional[dict] = None,
    bullets_list: Optional[List] = None,
    skills_list: Optional[List] = None
    ):
    """
    Serializes an Experience instance for detailed view within a resume context.
    Applies field overrides and uses pre-resolved bullets and skills.
    """
    if not experience_instance:
        return None

    overrides = field_overrides_dict or {}

    data = {
        'id': str(experience_instance.id),
        'user_id': str(experience_instance.user_id),
        'role': get_resolved_field(experience_instance, overrides, 'role'),
        'company': get_resolved_field(experience_instance, overrides, 'company'),
        'location': get_resolved_field(experience_instance, overrides, 'location'),
        'desc_long': get_resolved_field(experience_instance, overrides, 'desc_long')
    }

    # Handle dates
    raw_start_date = get_resolved_field(experience_instance, overrides, 'start')
    if isinstance(raw_start_date, (datetime.date, datetime.datetime)):
        data['start'] = raw_start_date.isoformat()
    else:
        data['start'] = raw_start_date

    raw_end_date = get_resolved_field(experience_instance, overrides, 'end')
    if isinstance(raw_end_date, (datetime.date, datetime.datetime)):
        data['end'] = raw_end_date.isoformat()
    else:
        data['end'] = raw_end_date
    
    return {
        "data": data,
        "bullets": bullets_list if bullets_list is not None else [],
        "skills": skills_list if skills_list is not None else []
    }

# General serializer for Experience
def serialize_experience(experience: Experience, include_bullets=False, include_skills=False):
    data = {
        'id': str(experience.id),
        'user_id': str(experience.user_id),
        'role': experience.role,
        'company': experience.company,
        'location': experience.location,
        'start_date': experience.start.isoformat() if experience.start is not None else None,
        'end_date': experience.end.isoformat() if experience.end is not None else None,
        'description': experience.desc_long,
    }
    if include_bullets:
        data['bullets'] = [{'order_index': b.order_index, 'content': b.content, 'id': str(b.id)} for b in experience.bullets]
    if include_skills:
        # Assuming a simple skill serialization for this context
        data['skills'] = [{'id': str(s.id), 'name': s.name} for s in experience.skills]
    return data

# --- CRUD Functions for Experience ---

def create_experience(user_id, data):
    """Creates a new experience entry for a user."""
    user = User.query.get_or_404(user_id)
    try:
        experience = Experience(
            user_id=user.id,
            role=data.get('role'),
            company=data.get('company'),
            location=data.get('location'),
            start=data.get('start_date'),
            end=data.get('end_date'),
            desc_long=data.get('desc_long')
        )
        db.session.add(experience)
        db.session.commit() # Commit to get experience.id

        # Handle bullets
        if 'bullets' in data and isinstance(data['bullets'], list):
            for idx, bullet_content in enumerate(data['bullets']):
                bullet = BulletPoint(
                    parent_id=experience.id,
                    parent_type=ParentType.experience,
                    order_index=idx,
                    content=bullet_content
                )
                db.session.add(bullet)
        
        # Handle skills (assuming data['skill_ids'] is a list of skill UUIDs)
        if 'skill_ids' in data and isinstance(data['skill_ids'], list):
            for skill_id in data['skill_ids']:
                skill = Skill.query.get(skill_id)
                if skill:
                    experience.skills.append(skill)
        
        db.session.commit()
        return serialize_experience(experience, include_bullets=True, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating experience: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for experience creation: {str(e)}")


def get_experience(experience_id, include_bullets=False, include_skills=False):
    """Gets a specific experience entry by ID."""
    query = Experience.query
    if include_bullets:
        query = query.options(joinedload(Experience.bullets))
    if include_skills:
        query = query.options(joinedload(Experience.skills))
    experience = query.get_or_404(experience_id)
    return serialize_experience(experience, include_bullets=include_bullets, include_skills=include_skills)


def get_all_experiences_for_user(user_id, include_bullets=False, include_skills=False):
    """Gets all experience entries for a specific user."""
    user = User.query.get_or_404(user_id)
    query = Experience.query.filter_by(user_id=user.id)
    if include_bullets:
        query = query.options(joinedload(Experience.bullets))
    if include_skills:
        query = query.options(joinedload(Experience.skills))
    experiences = query.order_by(Experience.start.desc().nullslast(), Experience.end.desc().nullslast()).all()
    return [serialize_experience(e, include_bullets=include_bullets, include_skills=include_skills) for e in experiences]


def update_experience(experience_id, data):
    """Updates an existing experience entry."""
    experience = Experience.query.options(
        joinedload(Experience.bullets), 
        joinedload(Experience.skills)
    ).get_or_404(experience_id)
    try:
        if 'role' in data: experience.role = data['role']
        if 'company' in data: experience.company = data['company']
        if 'location' in data: experience.location = data['location']
        if 'start_date' in data: experience.start = data['start_date']
        if 'end_date' in data: experience.end = data['end_date']
        if 'desc_long' in data: experience.desc_long = data['desc_long']

        if 'bullets' in data and isinstance(data['bullets'], list):
            BulletPoint.query.filter_by(parent_id=experience.id, parent_type=ParentType.experience).delete()
            for idx, bullet_content in enumerate(data['bullets']):
                db.session.add(BulletPoint(parent_id=experience.id, parent_type=ParentType.experience, order_index=idx, content=bullet_content))

        if 'skill_ids' in data and isinstance(data['skill_ids'], list):
            experience.skills.clear() # Remove existing skills
            for skill_id in data['skill_ids']:
                skill = Skill.query.get(skill_id)
                if skill:
                    experience.skills.append(skill)
        
        db.session.commit()
        updated_experience = Experience.query.options(joinedload(Experience.bullets), joinedload(Experience.skills)).get(experience_id)
        return serialize_experience(updated_experience, include_bullets=True, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating experience: {str(e)}")


def delete_experience(experience_id):
    """Deletes an experience entry."""
    experience = Experience.query.get_or_404(experience_id)
    try:
        db.session.delete(experience) # Bullets and skill associations should cascade
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
        return serialize_experience(experience, include_skills=True)
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
        return serialize_experience(experience, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing skill from experience: {str(e)}") 