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

def serialize_project(
    project_instance: Project, 
    field_overrides_dict: Optional[dict] = None,
    include_bullets_if_no_override: bool = False,
    include_skills_if_no_override: bool = False
    ):
    """
    Serializes a Project instance.
    If field_overrides_dict is provided, applies overrides and returns only resolved data fields.
    Otherwise, serializes global data and can include bullets/skills based on flags.
    """
    if not project_instance:
        return None

    overrides = field_overrides_dict or {}
    is_resume_context = bool(field_overrides_dict)

    data = {
        'id': str(project_instance.id),
        'user_id': str(project_instance.user_id),
        'title': get_resolved_field(project_instance, overrides, 'title', project_instance.title),
        'role': get_resolved_field(project_instance, overrides, 'role', project_instance.role),
        'desc_long': get_resolved_field(project_instance, overrides, 'desc_long', project_instance.desc_long)
    }
    
    raw_start_date = get_resolved_field(project_instance, overrides, 'start', project_instance.start)
    if isinstance(raw_start_date, (datetime.date, datetime.datetime)):
        data['start'] = raw_start_date.isoformat()
    else:
        data['start'] = raw_start_date

    raw_end_date = get_resolved_field(project_instance, overrides, 'end', project_instance.end)
    if isinstance(raw_end_date, (datetime.date, datetime.datetime)):
        data['end'] = raw_end_date.isoformat()
    else:
        data['end'] = raw_end_date
    
    if not is_resume_context:
        if include_bullets_if_no_override:
            data['bullets'] = [b.content for b in project_instance.bullets]
        if include_skills_if_no_override:
            data['skills'] = [{'id': str(s.id), 'name': s.name, 'category': s.category.value if s.category else None} for s in project_instance.skills]
            
    return data

# CRUD Functions for Project 

def create_project(user_id: UUID, data: dict):
    """Creates a new project entry for a user."""
    user = User.query.get_or_404(user_id)
    try:
        project = Project(
            user_id=user.id,
            title=data.get('title'),
            role=data.get('role'),
            start=data.get('start_date'),
            end=data.get('end_date'),
            desc_long=data.get('desc_long'),
            # description_field=data.get('description') # If added
        )
        db.session.add(project)
        db.session.flush() # To get project.id for bullets

        if 'bullets' in data and isinstance(data['bullets'], list):
            if not all(isinstance(b, str) for b in data['bullets']):
                raise ValueError("All items in 'bullets' list must be strings.")
            for idx, bullet_content in enumerate(data['bullets']):
                db.session.add(BulletPoint(parent_id=project.id, parent_type=ParentType.project, order_index=idx, content=bullet_content))
        
        if 'skill_ids' in data and isinstance(data['skill_ids'], list):
            for skill_id in data['skill_ids']:
                skill = Skill.query.get(skill_id)
                if skill:
                    project.skills.append(skill)
        
        db.session.commit()
        return serialize_project(project) # Ensure this serializes bullets as an ordered list
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating project: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for project creation: {str(e)}")


def get_project(project_id, include_bullets=False, include_skills=False):
    """Retrieves a specific project entry."""
    options = []
    if include_bullets:
        options.append(joinedload(Project.bullets))
    if include_skills:
        options.append(joinedload(Project.skills))
        
    project = Project.query.options(*options).get_or_404(project_id)
    return serialize_project(
        project, 
        include_bullets_if_no_override=include_bullets, 
        include_skills_if_no_override=include_skills
    )


def get_all_projects_for_user(user_id, include_bullets=False, include_skills=False):
    """Retrieves all project entries for a given user."""
    user = User.query.get_or_404(user_id)
    options = []
    if include_bullets:
        options.append(joinedload(Project.bullets))
    if include_skills:
        options.append(joinedload(Project.skills))
        
    projects = Project.query.options(*options).filter_by(user_id=user_id).all()
    return [serialize_project(
                proj, 
                include_bullets_if_no_override=include_bullets, 
                include_skills_if_no_override=include_skills
            ) for proj in projects]


def update_project(project_id: UUID, data: dict):
    """Updates an existing project entry."""
    project = get_or_404(Project, project_id, "Project")
    try:
        if 'title' in data: project.title = data['title']
        if 'role' in data: project.role = data['role']
        if 'start_date' in data: project.start = data['start_date']
        if 'end_date' in data: project.end = data['end_date']
        if 'desc_long' in data: project.desc_long = data['desc_long']
        # if 'description' in data: project.description_field = data['description']

        if 'bullets' in data: # If 'bullets' key is present, we replace all existing bullets
            if not isinstance(data['bullets'], list) or not all(isinstance(b, str) for b in data['bullets']):
                raise ValueError("If 'bullets' is provided for update, it must be a list of strings.")
            
            # Delete existing bullets
            BulletPoint.query.filter_by(parent_id=project.id, parent_type=ParentType.project.value).delete()
            # Add new bullets
            for idx, bullet_content in enumerate(data['bullets']):
                if bullet_content: # Add only non-empty bullets
                    db.session.add(BulletPoint(parent_id=project.id, parent_type=ParentType.project.value, order_index=idx, content=bullet_content))

        if 'skill_ids' in data and isinstance(data['skill_ids'], list):
            project.skills.clear()
            for skill_id in data['skill_ids']:
                skill = Skill.query.get(skill_id)
                if skill:
                    project.skills.append(skill)
        
        db.session.commit()
        updated_project = Project.query.options(joinedload(Project.bullets), joinedload(Project.skills)).get(project_id)
        return serialize_project(updated_project, include_bullets_if_no_override=True, include_skills_if_no_override=True)
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
    project = Project.query.options(joinedload(Project.skills)).get_or_404(project_id)
    skill = Skill.query.get_or_404(skill_id)
    try:
        if skill not in project.skills:
            project.skills.append(skill)
            db.session.commit()
        return serialize_project(project, include_skills_if_no_override=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error adding skill to project: {str(e)}")

def remove_skill_from_project(project_id, skill_id):
    project = Project.query.options(joinedload(Project.skills)).get_or_404(project_id)
    skill = Skill.query.get_or_404(skill_id)
    try:
        if skill in project.skills:
            project.skills.remove(skill)
            db.session.commit()
        return serialize_project(project, include_skills_if_no_override=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing skill from project: {str(e)}") 