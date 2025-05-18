from ..models import db, Resume, ResumeSection, ResumeItem, ResumeBullet, Skill
from ..models.models import Education, Experience, Project, BulletPoint, ResumeItemType, User, Template
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, undefer, Session as SQLAlchemySession
from sqlalchemy.orm.scoping import scoped_session
from uuid import UUID
from .utils import get_or_404, get_resolved_field

# Import the new serializer functions
from .education_controller import serialize_education_detail
from .experience_controller import serialize_experience_detail
from .project_controller import serialize_project_detail
from .bullet_point_controller import serialize_bullet_point as serialize_global_bullet_point
from .skill_controller import serialize_skill as serialize_global_skill

import datetime
import enum

# Helper function to fetch the global item
def _get_global_item(item_type: ResumeItemType, item_id: UUID):
    """Fetches the global item (Education, Experience, Project) based on type and ID."""
    session = db.session
    if item_type == ResumeItemType.education:
        return session.query(Education).options(
            joinedload(Education.bullets) # Eager load for diffing
        ).get(item_id)
    elif item_type == ResumeItemType.experience:
        return session.query(Experience).options(
            joinedload(Experience.bullets), # Eager load for diffing
            joinedload(Experience.skills)   # Eager load for diffing
        ).get(item_id)
    elif item_type == ResumeItemType.project:
        return session.query(Project).options(
            joinedload(Project.bullets), # Eager load for diffing
            joinedload(Project.skills)   # Eager load for diffing
        ).get(item_id)
    return None

def get_all_resumes(user_id=None):
    """Get all resumes, optionally filtered by user_id"""
    query = Resume.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    resumes = query.all()
    return [serialize_resume(resume) for resume in resumes]

def get_resume(resume_id):
    """Get a specific resume with all its sections and items"""
    resume = Resume.query.options(
        joinedload(Resume.sections),
        joinedload(Resume.items).joinedload(ResumeItem.resume_bullets)
    ).get_or_404(resume_id)
    return serialize_resume(resume, include_details=True)

def create_resume(data):
    """Create a new resume"""
    try:
        resume = Resume(
            user_id=data['user_id'],
            title=data.get('title', 'Untitled Resume'),
            template_id=data.get('template_id')
        )
        db.session.add(resume)
        db.session.commit()
        return serialize_resume(resume)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def update_resume(resume_id, data):
    """Update resume details"""
    resume = Resume.query.get_or_404(resume_id)
    
    if 'title' in data:
        resume.title = data['title']
    if 'template_id' in data:
        resume.template_id = data['template_id']
    
    db.session.commit()
    return serialize_resume(resume)

def delete_resume(resume_id):
    """Delete a resume"""
    resume = Resume.query.get_or_404(resume_id)
    db.session.delete(resume)
    db.session.commit()

def reorder_sections(resume_id, order_data):
    """Reorder sections in a resume"""
    resume = Resume.query.get_or_404(resume_id)
    
    # Update order_index for each section
    for section_order in order_data['sections']:
        section = ResumeSection.query.filter_by(
            resume_id=resume_id, 
            section_type=section_order['section_type']
        ).first()
        
        if section:
            section.order_index = section_order['order_index']
    
    db.session.commit()

def reorder_bullets(resume_id, item_type_str, item_id, order_data):
    """Reorder bullets for a resume item.
    item_type_str is the string representation of ResumeItemType enum, e.g., 'experience'.
    order_data should be a list of {'bullet_content': str, 'new_order_index': int }
    or {'existing_bullet_identifier': value, 'new_order_index': int}
    This function assumes order_data provides the *complete new set and order* of ResumeBullets.
    """
    try:
        item_type_enum = ResumeItemType[item_type_str]
    except KeyError:
        raise ValueError(f"Invalid item_type: {item_type_str}")

    resume_item = ResumeItem.query.filter_by(
        resume_id=resume_id,
        item_type=item_type_enum,
        item_id=item_id
    ).first_or_404()

    try:
        # Delete existing ResumeBullets for this item
        ResumeBullet.query.filter_by(
            resume_id=resume_id,
            item_type=item_type_enum,
            item_id=item_id
        ).delete()
        
        # Create new ResumeBullets based on order_data
        # order_data is expected to be a list of dicts, e.g., [{'content': '...', 'order_index': 0}, ...]
        # For simplicity, let's assume order_data is a list of bullet contents in the new desired order.
        # A more robust 'order_data' would include identifiers if reordering existing bullets.
        # If 'order_data' is just a list of contents:
        if 'bullets' in order_data and isinstance(order_data['bullets'], list):
            for index, bullet_content_or_obj in enumerate(order_data['bullets']):
                content = None
                # If order_data['bullets'] is a list of strings (content)
                if isinstance(bullet_content_or_obj, str):
                    content = bullet_content_or_obj
                # If order_data['bullets'] is a list of dicts like {'content': '...', 'order_index': N}
                elif isinstance(bullet_content_or_obj, dict) and 'content' in bullet_content_or_obj:
                    content = bullet_content_or_obj['content']
                    # Potentially use 'order_index' from bullet_content_or_obj if provided and reliable
                
                if content is not None:
                    new_bullet = ResumeBullet(
                        resume_id=resume_id,
                        item_type=item_type_enum,
                        item_id=item_id,
                        order_index=index, # Use the list index as the new order_index
                        content=content
                    )
                    db.session.add(new_bullet)
        
        db.session.commit()
        # Return the updated resume item detail or the full resume
        return serialize_resume_item_detail(resume_item) # Need to reload resume_item to get new bullets
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error reordering bullets: {str(e)}")

def serialize_bullet(bullet_instance, is_override: bool):
    """Serializes a ResumeBullet or a global BulletPoint."""
    return {
        'id': str(bullet_instance.id) if hasattr(bullet_instance, 'id') and not is_override else None, # Global bullets have IDs
        'resume_bullet_id': str(bullet_instance.id) if hasattr(bullet_instance, 'id') and is_override else None, # Placeholder if ResumeBullet gets its own ID
        'order_index': bullet_instance.order_index,
        'content': bullet_instance.content,
        'is_override': is_override
    }

def serialize_resume_item_detail(resume_item_entry: ResumeItem):
    """
    Serializes a ResumeItem with its details, applying overrides.
    This function now orchestrates fetching global data and applying
    ResumeItem-specific overrides for fields, bullets, and skills.
    """
    item_detail_scaffold = {
        'resume_id': str(resume_item_entry.resume_id),
        'item_type': resume_item_entry.item_type.value,
        'item_id': str(resume_item_entry.item_id),
        'order_index': resume_item_entry.order_index,
        'data': {},
        'bullets': [],
        'skills': [] # Add skills to the scaffold
    }

    global_item = None
    # Fetch the corresponding global item (Education, Experience, Project)
    if resume_item_entry.item_type.value == ResumeItemType.education:
        global_item = Education.query.options(
            joinedload(Education.bullets) # Eager load global bullets
        ).get(resume_item_entry.item_id)
    elif resume_item_entry.item_type.value == ResumeItemType.experience:
        global_item = Experience.query.options(
            joinedload(Experience.bullets), # Eager load global bullets
            joinedload(Experience.skills)  # Eager load global skills
        ).get(resume_item_entry.item_id)
    elif resume_item_entry.item_type.value == ResumeItemType.project:
        global_item = Project.query.options(
            joinedload(Project.bullets), # Eager load global bullets
            joinedload(Project.skills)  # Eager load global skills
        ).get(resume_item_entry.item_id)
    # Add other item types here

    if not global_item:
        item_detail_scaffold['data']['error'] = f"Global item {resume_item_entry.item_id} of type {resume_item_entry.item_type.value} not found."
        return item_detail_scaffold

    # --- Resolve Field Overrides ---
    field_overrides_dict = resume_item_entry.field_overrides.value if resume_item_entry.field_overrides is not None else {}

    # --- Resolve Bullets ---
    resolved_bullets = []
    overridden_bullets = ResumeBullet.query.filter_by(
        resume_id=resume_item_entry.resume_id,
        item_type=resume_item_entry.item_type,
        item_id=resume_item_entry.item_id
    ).order_by(ResumeBullet.order_index).all()

    if overridden_bullets:
        resolved_bullets = [serialize_bullet(b, is_override=True) for b in overridden_bullets]
    elif global_item and hasattr(global_item, 'bullets'): # Check if global_item is not None and has bullets
        # global_item.bullets should already be ordered by the relationship definition or an explicit order_by in the query
        resolved_bullets = [serialize_global_bullet_point(b) for b in global_item.bullets] # Use imported global serializer

    # --- Resolve Skills ---
    resolved_skills = []
    # Check for overridden skills first
    # Ensure overridden_skills are loaded, e.g. via joinedload in the initial query for resume_item_entry
    if resume_item_entry.overridden_skills: # This is the many-to-many relationship
        resolved_skills = [serialize_global_skill(skill) for skill in resume_item_entry.overridden_skills]
        # Add an 'is_override': True marker if needed by frontend, though context implies it
    elif global_item and hasattr(global_item, 'skills') and global_item.skills:
        resolved_skills = [serialize_global_skill(skill) for skill in global_item.skills]


    # --- Dispatch to specific serializer ---
    serialized_item_content = None
    if resume_item_entry.item_type.value == ResumeItemType.experience:
        serialized_item_content = serialize_experience_detail(global_item, field_overrides_dict, resolved_bullets, resolved_skills)
    elif resume_item_entry.item_type.value == ResumeItemType.project:
        serialized_item_content = serialize_project_detail(global_item, field_overrides_dict, resolved_bullets, resolved_skills)
    elif resume_item_entry.item_type.value == ResumeItemType.education:
        # Education might not have skills, pass None or empty list
        serialized_item_content = serialize_education_detail(global_item, field_overrides_dict, resolved_bullets, []) # Pass empty list for skills

    if serialized_item_content:
        item_detail_scaffold['data'] = serialized_item_content.get('data', {})
        item_detail_scaffold['bullets'] = serialized_item_content.get('bullets', [])
        item_detail_scaffold['skills'] = serialized_item_content.get('skills', []) # Get skills from specific serializer
    else:
        item_detail_scaffold['data']['error'] = f"Serializer not found or failed for item type {resume_item_entry.item_type.value}."

    return item_detail_scaffold

def serialize_resume(resume, include_details=False):
    """Convert a resume object to a dictionary"""
    result = {
        'id': str(resume.id),
        'user_id': str(resume.user_id),
        'title': resume.title,
        'template_id': str(resume.template_id) if resume.template_id else None,
        'created_at': resume.created_at.isoformat() if resume.created_at else None
    }
    
    if include_details:
        # Add sections with their order
        ordered_sections = sorted(resume.sections, key=lambda s: s.order_index)
        result['sections'] = [
            {
                'section_type': section.section_type,
                'order_index': section.order_index
            }
            for section in ordered_sections
        ]
        
        # Add items with their full details
        ordered_items = sorted(resume.items, key=lambda i: i.order_index)
        result['items'] = [
            serialize_resume_item_detail(item_entry)
            for item_entry in ordered_items
        ]
    
    return result

# ResumeItem Management 

def add_item_to_resume(resume_id, data):
    """Adds a global item (Education, Experience, Project) to a resume."""
    resume = Resume.query.get_or_404(resume_id)
    try:
        item_type_str = data['item_type']
        item_id = data['item_id'] # ID of the global Education, Experience, or Project
        
        try:
            item_type_enum = ResumeItemType[item_type_str]
        except KeyError:
            raise ValueError(f"Invalid item_type: {item_type_str}")

        # Validate the global item exists
        global_item_model = None
        if item_type_enum == ResumeItemType.education: global_item_model = Education
        elif item_type_enum == ResumeItemType.experience: global_item_model = Experience
        elif item_type_enum == ResumeItemType.project: global_item_model = Project
        # Add other types (publication, award)
        
        if not global_item_model or not global_item_model.query.get(item_id):
            raise ValueError(f"Global {item_type_str} with ID {item_id} not found.")

        # Check if item already exists in resume to prevent duplicates
        existing_resume_item = ResumeItem.query.filter_by(
            resume_id=resume_id,
            item_type=item_type_enum,
            item_id=item_id
        ).first()
        if existing_resume_item:
            raise ValueError(f"{item_type_str.capitalize()} with ID {item_id} already exists in this resume.")

        order_index = data.get('order_index')
        if order_index is None:
            max_order = db.session.query(db.func.max(ResumeItem.order_index)).filter_by(resume_id=resume_id).scalar()
            order_index = (max_order or -1) + 1
            
        resume_item = ResumeItem(
            resume_id=resume.id,
            item_type=item_type_enum,
            item_id=item_id,
            order_index=order_index,
            custom_desc=data.get('custom_desc')
        )
        db.session.add(resume_item)
        db.session.commit()
        return serialize_resume_item_detail(resume_item) # Or return the full updated resume
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error adding item to resume: {str(e)}")
    except (KeyError, ValueError) as e:
        db.session.rollback()
        raise ValueError(f"Invalid data for adding item to resume: {str(e)}")


def remove_item_from_resume(resume_id, item_type_str, item_id):
    """Removes a global item from a resume."""
    resume = Resume.query.get_or_404(resume_id)
    try:
        item_type_enum = ResumeItemType[item_type_str]
    except KeyError:
        raise ValueError(f"Invalid item_type: {item_type_str}")

    resume_item = ResumeItem.query.filter_by(
        resume_id=resume.id,
        item_type=item_type_enum,
        item_id=item_id
    ).first_or_404()
    
    try:
        # ResumeBullets associated with this ResumeItem will be cascade deleted
        db.session.delete(resume_item)
        db.session.commit()
        return {"message": f"{item_type_str.capitalize()} item removed from resume."}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing item from resume: {str(e)}")


def update_resume_item(resume_id: UUID, item_type_str: str, item_id: UUID, data: dict):
    """
    Updates a specific item within a resume.
    The request body 'data' should contain the full desired state of the item's
    content (fields, bullets, skills).
    The backend will diff this against the global item to determine overrides.
    """
    session = db.session  
    try:
        item_type_enum = ResumeItemType(item_type_str)
    except ValueError:
        raise ValueError(f"Invalid item_type: {item_type_str}")

    resume_item = session.query(ResumeItem).options(
        joinedload(ResumeItem.resume_bullets),
        joinedload(ResumeItem.overridden_skills) # Eager load for diffing
    ).filter_by(
        resume_id=resume_id,
        item_type=item_type_enum,
        item_id=item_id
    ).first()

    if not resume_item:
        raise ValueError(f"ResumeItem not found for resume {resume_id}, type {item_type_str}, item {item_id}")

    global_item = _get_global_item(item_type_enum, item_id)
    if not global_item:
        raise ValueError(f"Global {item_type_str} item with ID {item_id} not found.")

    # --- Start Diffing and Updating ---
    current_field_overrides = dict(resume_item.field_overrides.value if resume_item.field_overrides is not None else {}) # Make a mutable copy
    field_overrides_changed = False

    # Submitted data for simple fields (e.g., title, role, dates, desc_long)
    # This comes from data['content']['data'] in the request payload
    submitted_fields_data = data.get('content', {}).get('data', {})

    # Dynamically process fields from submitted_fields_data
    for field_name, submitted_value in submitted_fields_data.items():
        # Skip non-overridable identifiers or fields not present on the global model
        if field_name in ['id', 'user_id'] or not hasattr(global_item, field_name):
            if field_name not in ['id', 'user_id']:
                 print(f"Warning: Submitted field '{field_name}' not found on global item {global_item.id} of type {item_type_str}. Skipping override.")
            continue

        global_value = getattr(global_item, field_name)
        comparable_global_value = global_value

        # Normalize global_value for comparison if it's a date or other special type
        if isinstance(global_value, (datetime.date, datetime.datetime)) and global_value is not None:
            comparable_global_value = global_value.isoformat()
        # Add other type normalizations if necessary (e.g., Enums to .value, Decimals to str)
        # elif isinstance(global_value, enum.Enum):
        #     comparable_global_value = global_value.value

        # If submitted_value is different from global_value, it's an override
        if submitted_value != comparable_global_value:
            # Only update if the new submitted_value is different from the current override for this field
            if current_field_overrides.get(field_name) != submitted_value:
                current_field_overrides[field_name] = submitted_value
                field_overrides_changed = True
        # If submitted_value is same as global_value, but an override exists, remove the override
        elif field_name in current_field_overrides:
            del current_field_overrides[field_name]
            field_overrides_changed = True
    
    if field_overrides_changed:
        if not current_field_overrides: # If all overrides were removed
            resume_item.field_overrides = {} # Assign an empty dict instead of None
        else:
            resume_item.field_overrides = current_field_overrides
        session.add(resume_item)


    # --- Handle Bullet Overrides ---
    submitted_bullets_data = data.get('content', {}).get('bullets', []) # Expect list of dicts: [{'content': '...', 'order_index': N}, ...]
    global_bullets_query = session.query(BulletPoint).filter_by(parent_id=global_item.id, parent_type=global_item.bullet_parent_type).order_by(BulletPoint.order_index)
    
    # Check if submitted bullets differ from global bullets
    bullets_differ = _compare_bullet_lists(submitted_bullets_data, global_bullets_query.all())

    if bullets_differ:
        # Clear existing overridden bullets for this ResumeItem
        session.query(ResumeBullet).filter_by(resume_id=resume_item.resume_id, item_type=resume_item.item_type, item_id=resume_item.item_id).delete(synchronize_session=False)
        # Add new overridden bullets
        for idx, bullet_data in enumerate(submitted_bullets_data):
            # Ensure bullet_data has 'content'; 'order_index' from submitted data or use loop index
            order_idx = bullet_data.get('order_index', idx)
            content = bullet_data.get('content')
            if content is not None: # Only add bullets with content
                new_bullet = ResumeBullet(
                    resume_id=resume_item.resume_id,
                    item_type=resume_item.item_type,
                    item_id=resume_item.item_id,
                    order_index=order_idx,
                    content=content
                )
                session.add(new_bullet)
    else: # Bullets are same as global, remove any existing overrides
        if session.query(ResumeBullet).filter_by(resume_id=resume_item.resume_id, item_type=resume_item.item_type, item_id=resume_item.item_id).count() > 0:
            session.query(ResumeBullet).filter_by(resume_id=resume_item.resume_id, item_type=resume_item.item_type, item_id=resume_item.item_id).delete(synchronize_session=False)

    # --- Handle Skill Overrides ---
    # Frontend sends list of skill objects: [{'id': 'skill_uuid', 'name': 'Skill Name'}, ...]
    # We only care about the IDs for diffing and storing.
    submitted_skill_ids = [skill_data.get('id') for skill_data in data.get('content', {}).get('skills', []) if skill_data.get('id')]

    if hasattr(global_item, 'skills'): # Check if global item type supports skills
        global_skills_query = global_item.skills # Assuming this is the relationship yielding Skill objects
        
        skills_differ = _compare_skill_id_lists(submitted_skill_ids, global_skills_query)

        if skills_differ:
            # Clear existing overridden skills for this ResumeItem
            resume_item.overridden_skills.clear() # Assuming 'overridden_skills' is the association proxy or relationship
            # Add new overridden skills
            for skill_id_str in submitted_skill_ids:
                try:
                    skill_id_uuid = UUID(skill_id_str)
                    skill = session.query(Skill).get(skill_id_uuid)
                    if skill:
                        resume_item.overridden_skills.append(skill)
                    else:
                        print(f"Warning: Submitted skill ID {skill_id_str} not found. Skipping.")
                except ValueError:
                    print(f"Warning: Invalid UUID format for skill ID {skill_id_str}. Skipping.")
        else: # Skills are same as global, remove any existing skill overrides
            if resume_item.overridden_skills:
                 resume_item.overridden_skills.clear()
    
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        # Log the detailed error e
        raise ValueError(f"Database error updating resume item: {str(e)}")

    # Re-fetch and serialize the updated item to return the latest state
    # Ensure the session is clean or use a new session for fetching if necessary
    updated_resume_item_entry = session.query(ResumeItem).options(
        joinedload(ResumeItem.resume_bullets),
        joinedload(ResumeItem.overridden_skills)
    ).get(resume_item.id) # Use the primary key of ResumeItem
    
    assert updated_resume_item_entry is not None
    
    return serialize_resume_item_detail(updated_resume_item_entry)

def reorder_resume_items(resume_id, order_data):
    """Reorders items within a resume.
    order_data is expected to be a list of dicts:
    [{'item_type': 'experience', 'item_id': 'uuid', 'order_index': 0}, ...]
    """
    Resume.query.get_or_404(resume_id) # Validate resume exists
    try:
        for item_order in order_data.get('items', []):
            try:
                item_type_enum = ResumeItemType[item_order['item_type']]
            except KeyError:
                # Skip or raise error for invalid item_type
                print(f"Warning: Invalid item_type '{item_order['item_type']}' in reorder_resume_items. Skipping.")
                continue

            resume_item = ResumeItem.query.filter_by(
                resume_id=resume_id,
                item_type=item_type_enum,
                item_id=item_order['item_id']
            ).first()
            
            if resume_item:
                resume_item.order_index = item_order['order_index']
            else:
                # Optionally, handle items not found (e.g., log warning)
                print(f"Warning: ResumeItem not found for reordering: {item_order}. Skipping.")

        db.session.commit()
        return get_resume(resume_id) # Return the full updated resume
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error reordering resume items: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing data for reordering resume items: {str(e)}")

def update_resume_sections_order(resume_id: UUID, sections_order_data: list):
    """
    Updates the order of sections within a resume.
    sections_order_data is expected to be a list of dictionaries,
    e.g., [{"id": "section_uuid", "order_index": 0}, ...]
    or just a list of section_ids in the new desired order.
    """
    try:
        resume = get_or_404(Resume, resume_id, "Resume")
        
        # Create a map of section_id to new order_index for efficient lookup
        new_order_map = {}
        for index, section_data_item in enumerate(sections_order_data):
            if isinstance(section_data_item, dict) and 'id' in section_data_item:
                section_id = section_data_item['id']
                # Use provided order_index if available, otherwise use list index
                order_index = section_data_item.get('order_index', index)
                new_order_map[str(section_id)] = order_index
            elif isinstance(section_data_item, (str, UUID)): # If it's just a list of IDs
                new_order_map[str(section_data_item)] = index
            else:
                raise ValueError("Invalid format for sections_order_data item.")

        updated_sections_count = 0
        for section in resume.sections: # Assuming resume.sections is the relationship
            if str(section.id) in new_order_map:
                section.order_index = new_order_map[str(section.id)]
                updated_sections_count += 1
        
        if updated_sections_count == 0 and len(sections_order_data) > 0:
            # This might mean none of the provided section IDs matched existing sections.
            # Depending on desired behavior, this could be an error or just a no-op.
            pass # Or raise ValueError("No matching sections found to reorder.")


        db.session.commit()
        # Reload or re-fetch resume to get sections in updated order for serialization
        db.session.refresh(resume) 
        # order should be handled by the Model relationship with order_by
        return serialize_resume(resume, include_details=True) #
        
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Database error updating resume sections order: {str(e)}")
    except ValueError as e: # Catch specific ValueErrors from logic above
        db.session.rollback()
        raise e

# --- Helper functions for diffing ---

def _compare_bullet_lists(submitted_bullets_data: list, global_bullets_query):
    """
    Compares a list of submitted bullet data (dicts) with a query of global BulletPoint objects.
    Returns True if they are different, False otherwise.
    Assumes submitted_bullets_data is like [{'content': '...', 'order_index': 0}, ...]
    Assumes global_bullets_query is sorted by order_index.
    """
    global_bullets_list = sorted(list(global_bullets_query), key=lambda b: b.order_index)

    if len(submitted_bullets_data) != len(global_bullets_list):
        return True
    for i, submitted_bullet in enumerate(submitted_bullets_data):
        global_bullet = global_bullets_list[i]
        # Compare content. Order is implicitly compared by list position after sorting.
        if submitted_bullet.get('content') != global_bullet.content:
            return True
    return False

def _compare_skill_id_lists(submitted_skill_ids: list, global_skills_query):
    """
    Compares a list of submitted skill IDs with a query of global Skill objects.
    Returns True if they are different, False otherwise.
    """
    global_skill_id_set = {str(skill.id) for skill in global_skills_query}
    submitted_skill_id_set = set(map(str, submitted_skill_ids)) # Ensure submitted IDs are strings

    return global_skill_id_set != submitted_skill_id_set

# --- Resume Section Management ---

def add_section_to_resume(resume_id: UUID, data: dict):
    """Adds a new section to a resume."""
    resume = get_or_404(Resume, resume_id, "Resume")
    
    title = data.get('title', 'Untitled Section')
    # Determine the next order_index for the new section
    max_order_index = db.session.query(db.func.max(ResumeSection.order_index)).filter_by(resume_id=resume_id).scalar()
    order_index = (max_order_index or -1) + 1

    try:
        section = ResumeSection(
            resume_id=resume_id,
            title=title,
            order_index=order_index
            # Add other fields like 'layout_type' if your model supports them
        )
        db.session.add(section)
        db.session.commit()
        # Serialize the section - you might need a serialize_resume_section function
        return {"id": str(section.id), "resume_id": str(section.resume_id), "title": section.title, "order_index": section.order_index}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error adding section to resume: {str(e)}")

def remove_section_from_resume(resume_id: UUID, section_id: UUID):
    """Removes a section from a resume."""
    section = get_or_404(ResumeSection, section_id, "ResumeSection")
    if section.resume_id != resume_id:
        raise ValueError("Section does not belong to the specified resume.")
    
    # Consider implications: what happens to ResumeItems in this section?
    # Option 1: Cascade delete (if model relationship is set up for it)
    # Option 2: Disassociate/move items (requires more logic)
    # Option 3: Prevent deletion if section contains items (add check here)
    # For now, assuming cascade or that items are handled/disallowed at a higher level or by DB constraints.

    try:
        db.session.delete(section)
        db.session.commit()
        return {"message": "Section removed successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing section from resume: {str(e)}")