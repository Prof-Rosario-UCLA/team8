from ..models import db, User, Project, BulletPoint, Skill, ParentType
from ..models.models import project_skills
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Optional, List
from uuid import UUID
from .skill_controller import serialize_skill
from .bullet_point_controller import serialize_bullet_point
from .utils import get_or_404, get_resolved_field
import datetime

def serialize_project(project: Project, include_bullets=False, include_skills=False):
    data = {
        'id': str(project.id),
        'user_id': str(project.user_id),
        'title': project.title,
        'role': project.role,
        'start_date': project.start.isoformat() if project.start is not None else None,
        'end_date': project.end.isoformat() if project.end is not None else None,
        # 'description': project.description_field, # Description later for LLM to get context
    }
    if include_bullets:
        data['bullets'] = [{'order_index': b.order_index, 'content': b.content, 'id': str(b.id)} for b in project.bullets]
    if include_skills:
        data['skills'] = [{'id': str(s.id), 'name': s.name} for s in project.skills]
    return data

def serialize_project_detail(
    project_instance: Project,
    field_overrides_dict: Optional[dict] = None,
    bullets_list: Optional[List] = None,
    skills_list: Optional[List] = None
    ):
    """
    Serializes a Project instance for detailed view within a resume context.
    Applies field overrides and uses pre-resolved bullets and skills.
    """
    if not project_instance:
        return None

    overrides = field_overrides_dict or {}

    data = {
        'id': str(project_instance.id),
        'user_id': str(project_instance.user_id),
        'title': get_resolved_field(project_instance, overrides, 'title'),
        'role': get_resolved_field(project_instance, overrides, 'role'),
        'desc_long': get_resolved_field(project_instance, overrides, 'desc_long')
    }
    
    # Handle dates
    raw_start_date = get_resolved_field(project_instance, overrides, 'start')
    if isinstance(raw_start_date, (datetime.date, datetime.datetime)):
        data['start'] = raw_start_date.isoformat()
    else:
        data['start'] = raw_start_date

    raw_end_date = get_resolved_field(project_instance, overrides, 'end')
    if isinstance(raw_end_date, (datetime.date, datetime.datetime)):
        data['end'] = raw_end_date.isoformat()
    else:
        data['end'] = raw_end_date
    
    return {
        "data": data,
        "bullets": bullets_list if bullets_list is not None else [],
        "skills": skills_list if skills_list is not None else []
    }

# CRUD Functions for Project 

def create_project(user_id, data):
    """Creates a new project entry for a user."""
    user = User.query.get_or_404(user_id)
    try:
        project = Project(
            user_id=user.id,
            title=data['title'],
            role=data.get('role'),
            start=data.get('start_date'),
            end=data.get('end_date'),
            desc_long=data.get('desc_long'),
            # description_field=data.get('description') # If added
        )
        db.session.add(project)
        db.session.commit() # Commit to get project.id

        if 'bullets' in data and isinstance(data['bullets'], list):
            for idx, bullet_content in enumerate(data['bullets']):
                db.session.add(BulletPoint(parent_id=project.id, parent_type=ParentType.project, order_index=idx, content=bullet_content))
        
        if 'skill_ids' in data and isinstance(data['skill_ids'], list):
            for skill_id in data['skill_ids']:
                skill = Skill.query.get(skill_id)
                if skill:
                    project.skills.append(skill)
        
        db.session.commit()
        return serialize_project(project, include_bullets=True, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating project: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for project creation: {str(e)}")


def get_project(project_id, include_bullets=False, include_skills=False):
    """Gets a specific project entry by ID."""
    query = Project.query
    if include_bullets:
        query = query.options(joinedload(Project.bullets))
    if include_skills:
        query = query.options(joinedload(Project.skills))
    project = query.get_or_404(project_id)
    return serialize_project(project, include_bullets=include_bullets, include_skills=include_skills)


def get_all_projects_for_user(user_id, include_bullets=False, include_skills=False):
    """Gets all project entries for a specific user."""
    user = User.query.get_or_404(user_id)
    query = Project.query.filter_by(user_id=user.id)
    if include_bullets:
        query = query.options(joinedload(Project.bullets))
    if include_skills:
        query = query.options(joinedload(Project.skills))
    projects = query.order_by(Project.start.desc().nullslast(), Project.end.desc().nullslast()).all()
    return [serialize_project(p, include_bullets=include_bullets, include_skills=include_skills) for p in projects]


def update_project(project_id, data):
    """Updates an existing project entry."""
    project = Project.query.options(
        joinedload(Project.bullets), 
        joinedload(Project.skills)
    ).get_or_404(project_id)
    try:
        if 'title' in data: project.title = data['title']
        if 'role' in data: project.role = data['role']
        if 'start_date' in data: project.start = data['start_date']
        if 'end_date' in data: project.end = data['end_date']
        if 'desc_long' in data: project.desc_long = data['desc_long']
        # if 'description' in data: project.description_field = data['description']

        if 'bullets' in data and isinstance(data['bullets'], list):
            BulletPoint.query.filter_by(parent_id=project.id, parent_type=ParentType.project).delete()
            for idx, bullet_content in enumerate(data['bullets']):
                db.session.add(BulletPoint(parent_id=project.id, parent_type=ParentType.project, order_index=idx, content=bullet_content))

        if 'skill_ids' in data and isinstance(data['skill_ids'], list):
            project.skills.clear()
            for skill_id in data['skill_ids']:
                skill = Skill.query.get(skill_id)
                if skill:
                    project.skills.append(skill)
        
        db.session.commit()
        updated_project = Project.query.options(joinedload(Project.bullets), joinedload(Project.skills)).get(project_id)
        return serialize_project(updated_project, include_bullets=True, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating project: {str(e)}")


def delete_project(project_id):
    """Deletes a project entry."""
    project = Project.query.get_or_404(project_id)
    try:
        db.session.delete(project)
        db.session.commit()
        return {"message": "Project entry deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting project: {str(e)}")

# --- Skill Association for Project ---
def add_skill_to_project(project_id, skill_id):
    project = Project.query.get_or_404(project_id)
    skill = Skill.query.get_or_404(skill_id)
    try:
        if skill not in project.skills:
            project.skills.append(skill)
            db.session.commit()
        return serialize_project(project, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error adding skill to project: {str(e)}")

def remove_skill_from_project(project_id, skill_id):
    project = Project.query.get_or_404(project_id)
    skill = Skill.query.get_or_404(skill_id)
    try:
        if skill in project.skills:
            project.skills.remove(skill)
            db.session.commit()
        return serialize_project(project, include_skills=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing skill from project: {str(e)}") 