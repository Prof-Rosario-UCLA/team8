from ..models import db, Resume, ResumeSection, ResumeItem, ResumeBullet, Skill
from ..models.models import (
    Education,
    Experience,
    Project,
    BulletPoint,
    ResumeItemType,
    User,
    Template,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    joinedload,
    undefer,
    Session as SQLAlchemySession,
    selectinload,
    make_transient,
)
from sqlalchemy import func
from uuid import UUID
from .utils import get_or_404, get_resolved_field

# Import serializer functions
from .education import serialize_education
from .experience import serialize_experience
from .project import serialize_project
from .skill import serialize_skill as serialize_global_skill

import datetime
import enum
from typing import Optional, List


# Helper function to fetch the global item
def _get_global_item(item_type: ResumeItemType, item_id: UUID):
    """Fetches the global item (Education, Experience, Project) based on type and ID."""
    session = db.session
    if item_type == ResumeItemType.education:
        return (
            session.query(Education)
            .options(
                joinedload(Education.bullets)  # Eager load for diffing
            )
            .get(item_id)
        )
    elif item_type == ResumeItemType.experience:
        return (
            session.query(Experience)
            .options(
                joinedload(Experience.bullets),  # Eager load for diffing
                joinedload(Experience.skills),  # Eager load for diffing
            )
            .get(item_id)
        )
    elif item_type == ResumeItemType.project:
        return (
            session.query(Project)
            .options(
                joinedload(Project.bullets),  # Eager load for diffing
                joinedload(Project.skills),  # Eager load for diffing
            )
            .get(item_id)
        )
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
        joinedload(Resume.sections)
        .selectinload(ResumeSection.items)
        .joinedload(ResumeItem.resume_bullets),
        joinedload(Resume.sections)
        .selectinload(ResumeSection.items)
        .selectinload(ResumeItem.overridden_skills),
    ).get_or_404(resume_id)
    return serialize_resume(resume, include_details=True)


def create_resume(data):
    """Create a new resume"""
    try:
        resume = Resume(
            user_id=data["user_id"],
            title=data.get("title", "Untitled Resume"),
            template_id=data.get("template_id"),
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

    if "title" in data:
        resume.title = data["title"]
    if "template_id" in data:
        resume.template_id = data["template_id"]

    db.session.commit()
    return serialize_resume(resume)


def delete_resume(resume_id):
    """Delete a resume"""
    resume = Resume.query.get_or_404(resume_id)
    db.session.delete(resume)
    db.session.commit()
    return {"message": "Resume deleted successfully"}


def reorder_sections(resume_id: UUID, section_type_order_list: list[str]):
    """
    Reorders sections in a resume based on a list of section type strings.
    Example: ["experience", "project", "education"]
    """
    resume = Resume.query.get_or_404(resume_id)

    # Create a map of section_type_enum to its new order_index
    new_order_map = {}
    for index, type_str in enumerate(section_type_order_list):
        try:
            section_type_enum = ResumeItemType[type_str]  # Convert string to enum
            new_order_map[section_type_enum] = index
        except KeyError:
            raise ValueError(f"Invalid section_type '{type_str}' in ordering list.")

    # Update existing sections
    updated_count = 0
    for section in resume.sections:
        if section.section_type in new_order_map:
            section.order_index = new_order_map[section.section_type]
            updated_count += 1
        else:
            # This section type was not in the new order list,
            # it might be orphaned or need to be handled (e.g., deleted or appended).
            # For now, we'll assume the list is comprehensive for reordering.
            # Alternatively, assign a high order_index to push it to the end.
            pass

    # Note: This doesn't create sections if they are in the list but not in DB.
    # That's typically handled by adding items or a dedicated "ensure sections exist" logic.

    try:
        db.session.commit()
        # Re-fetch to ensure data is current, especially order_index
        db.session.refresh(resume)
        return serialize_resume(resume, include_details=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Database error reordering sections: {str(e)}")


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
        resume_id=resume_id, item_type=item_type_enum, item_id=item_id
    ).first_or_404()

    try:
        # Delete existing ResumeBullets for this item
        ResumeBullet.query.filter_by(
            resume_id=resume_id, item_type=item_type_enum, item_id=item_id
        ).delete()

        # Create new ResumeBullets based on order_data
        # order_data is expected to be a list of dicts, e.g., [{'content': '...', 'order_index': 0}, ...]
        # For simplicity, let's assume order_data is a list of bullet contents in the new desired order.
        # A more robust 'order_data' would include identifiers if reordering existing bullets.
        # If 'order_data' is just a list of contents:
        if "bullets" in order_data and isinstance(order_data["bullets"], list):
            for index, bullet_content_or_obj in enumerate(order_data["bullets"]):
                content = None
                # If order_data['bullets'] is a list of strings (content)
                if isinstance(bullet_content_or_obj, str):
                    content = bullet_content_or_obj
                # If order_data['bullets'] is a list of dicts like {'content': '...', 'order_index': N}
                elif (
                    isinstance(bullet_content_or_obj, dict)
                    and "content" in bullet_content_or_obj
                ):
                    content = bullet_content_or_obj["content"]
                    # Potentially use 'order_index' from bullet_content_or_obj if provided and reliable

                if content is not None:
                    new_bullet = ResumeBullet(
                        resume_id=resume_id,
                        item_type=item_type_enum,
                        item_id=item_id,
                        order_index=index,  # Use the list index as the new order_index
                        content=content,
                    )
                    db.session.add(new_bullet)

        db.session.commit()
        # Return the updated resume item detail or the full resume
        return serialize_resume_item_detail(
            resume_item
        )  # Need to reload resume_item to get new bullets
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error reordering bullets: {str(e)}")


def serialize_resume_item_detail(resume_item_entry: Optional[ResumeItem]):
    """
    Serializes a ResumeItem with its details, applying overrides.
    Bullets will be serialized as a list of strings.
    """
    if not resume_item_entry:
        return None  # Or an appropriate error/empty structure

    item_detail_scaffold = {
        "resume_id": str(resume_item_entry.resume_id),
        "item_type": resume_item_entry.item_type.value,
        "item_id": str(resume_item_entry.item_id),
        "order_index": resume_item_entry.order_index,
        "data": {},
        "bullets": [],
        "skills": [],  # Add skills to the scaffold
    }

    global_item = None
    # Fetch the corresponding global item (Education, Experience, Project)
    if resume_item_entry.item_type.value == ResumeItemType.education:
        global_item = Education.query.options(
            joinedload(Education.bullets)  # Eager load global bullets
        ).get(resume_item_entry.item_id)
    elif resume_item_entry.item_type.value == ResumeItemType.experience:
        global_item = Experience.query.options(
            joinedload(Experience.bullets),  # Eager load global bullets
            joinedload(Experience.skills),  # Eager load global skills
        ).get(resume_item_entry.item_id)
    elif resume_item_entry.item_type.value == ResumeItemType.project:
        global_item = Project.query.options(
            joinedload(Project.bullets),  # Eager load global bullets
            joinedload(Project.skills),  # Eager load global skills
        ).get(resume_item_entry.item_id)
    # Add other item types here

    if not global_item:
        item_detail_scaffold["data"]["error"] = (
            f"Global item {resume_item_entry.item_id} of type {resume_item_entry.item_type.value} not found."
        )
        return item_detail_scaffold

    #  Resolve Field Overrides
    field_overrides_dict = (
        resume_item_entry.field_overrides.value
        if resume_item_entry.field_overrides is not None
        else {}
    )

    #  Resolve Bullets
    resolved_bullets_list_of_strings: List[str] = []

    # Query for overridden bullets, ensuring they are ordered
    # The relationship ResumeItem.bullets is already ordered by ResumeBullet.order_index
    # but if accessing ResumeBullet directly, ensure order_by.
    # Let's use the relationship if available and loaded.
    # Assuming resume_item_entry.bullets is eager loaded with order_by.

    # Check if bullets were eager loaded via the relationship
    if (
        "bullets" in resume_item_entry.__dict__ and resume_item_entry.bullets
    ):  # Accessing via loaded relationship
        resolved_bullets_list_of_strings = [
            b.content for b in resume_item_entry.bullets
        ]
    else:  # Fallback to query if not loaded or to be absolutely sure of ordering here
        overridden_bullets_q = (
            ResumeBullet.query.filter_by(
                resume_id=resume_item_entry.resume_id,
                item_type=resume_item_entry.item_type,
                item_id=resume_item_entry.item_id,
            )
            .order_by(ResumeBullet.order_index)
            .all()
        )
        if overridden_bullets_q:
            resolved_bullets_list_of_strings = [b.content for b in overridden_bullets_q]
        elif global_item and hasattr(global_item, "bullets"):
            # Assuming global_item.bullets relationship is also defined with order_by
            resolved_bullets_list_of_strings = [b.content for b in global_item.bullets]

    #  Resolve Skills
    resolved_skills = []
    # Check for overridden skills first
    # Ensure overridden_skills are loaded, e.g. via joinedload in the initial query for resume_item_entry
    if resume_item_entry.overridden_skills:  # This is the many-to-many relationship
        resolved_skills = [
            serialize_global_skill(skill)
            for skill in resume_item_entry.overridden_skills
        ]
        # Add an 'is_override': True marker if needed by frontend, though context implies it
    elif global_item and hasattr(global_item, "skills") and global_item.skills:
        resolved_skills = [
            serialize_global_skill(skill) for skill in global_item.skills
        ]

    #  Dispatch to specific serializer
    serialized_item_data_fields = None  # This will now only contain the 'data' part
    if resume_item_entry.item_type.value == ResumeItemType.experience:
        serialized_item_data_fields = serialize_experience(
            global_item, field_overrides_dict=field_overrides_dict
        )
    elif resume_item_entry.item_type.value == ResumeItemType.project:
        serialized_item_data_fields = serialize_project(
            global_item, field_overrides_dict=field_overrides_dict
        )
    elif resume_item_entry.item_type.value == ResumeItemType.education:
        serialized_item_data_fields = serialize_education(
            global_item, field_overrides_dict=field_overrides_dict
        )

    if serialized_item_data_fields:
        item_detail_scaffold["data"] = serialized_item_data_fields
        item_detail_scaffold["bullets"] = resolved_bullets_list_of_strings
        item_detail_scaffold["skills"] = (
            resolved_skills  # This is already a list of serialized skill dicts
        )
    else:
        item_detail_scaffold["data"]["error"] = (
            f"Serializer not found or failed for item type {resume_item_entry.item_type.value}."
        )

    return item_detail_scaffold


def serialize_resume(resume: Resume, include_details=False):
    """Serializes a Resume, optionally including its sections and items."""
    data = {
        "id": str(resume.id),
        "user_id": str(resume.user_id),
        "title": resume.title,
        "template_id": str(resume.template_id)
        if resume.template_id is not None
        else None,
        "created_at": resume.created_at.isoformat(),
        "updated_at": resume.updated_at.isoformat(),
        "sections": [],
    }

    if include_details:
        serialized_sections = []
        # Ensure sections are ordered by order_index
        # The relationship Resume.sections should ideally be ordered.
        # If not, sort them: sorted_sections = sorted(resume.sections, key=lambda s: s.order_index)
        # For now, assuming resume.sections is already ordered or can be iterated directly
        # if eager loaded with order.

        # Explicitly sort sections if not guaranteed by relationship's order_by
        sorted_sections_list = sorted(resume.sections, key=lambda s: s.order_index)

        for section in sorted_sections_list:
            # Pass include_items=True to serialize items within each section
            s_data = serialize_resume_section(section, include_items=True)
            serialized_sections.append(s_data)
        data["sections"] = serialized_sections
    return data


# ResumeItem Management


def add_item_to_resume(resume_id, data):
    """Adds a global item (Education, Experience, Project) to a resume."""
    resume = Resume.query.get_or_404(resume_id)
    try:
        item_type_str = data["item_type"]
        item_id = data["item_id"]  # ID of the global Education, Experience, or Project

        try:
            item_type_enum = ResumeItemType[item_type_str]
        except KeyError:
            raise ValueError(f"Invalid item_type: {item_type_str}")

        # Validate the global item exists
        global_item_model = None
        if item_type_enum == ResumeItemType.education:
            global_item_model = Education
        elif item_type_enum == ResumeItemType.experience:
            global_item_model = Experience
        elif item_type_enum == ResumeItemType.project:
            global_item_model = Project
        # Add other types (publication, award)

        if not global_item_model or not global_item_model.query.get(item_id):
            raise ValueError(f"Global {item_type_str} with ID {item_id} not found.")

        # Check if item already exists in resume to prevent duplicates
        existing_resume_item = ResumeItem.query.filter_by(
            resume_id=resume_id, item_type=item_type_enum, item_id=item_id
        ).first()
        if existing_resume_item:
            raise ValueError(
                f"{item_type_str.capitalize()} with ID {item_id} already exists in this resume."
            )

        order_index = data.get("order_index")
        if order_index is None:
            max_order = (
                db.session.query(db.func.max(ResumeItem.order_index))
                .filter_by(resume_id=resume_id)
                .scalar()
            )
            order_index = (max_order or -1) + 1

        resume_item = ResumeItem(
            resume_id=resume.id,
            item_type=item_type_enum,
            item_id=item_id,
            order_index=order_index,
            custom_desc=data.get("custom_desc"),
        )
        db.session.add(resume_item)
        db.session.commit()
        return serialize_resume_item_detail(
            resume_item
        )  # Or return the full updated resume
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error adding item to resume: {str(e)}")
    except (KeyError, ValueError) as e:
        db.session.rollback()
        raise ValueError(f"Invalid data for adding item to resume: {str(e)}")


def remove_item_from_resume(resume_id: UUID, item_type_str: str, item_id: UUID):
    """Removes an item from a resume section."""
    try:
        item_type_enum = ResumeItemType[item_type_str]
    except KeyError:
        raise ValueError(f"Invalid item_type: {item_type_str}")

    resume_item = ResumeItem.query.filter_by(
        resume_id=resume_id,
        item_type=item_type_enum,  # This is the section type
        item_id=item_id,
    ).first_or_404(
        description=f"Item not found in section '{item_type_str}' for this resume."
    )

    try:
        db.session.delete(resume_item)
        db.session.commit()
        return {"message": "Item removed from resume successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error removing item from resume: {str(e)}")


def update_resume_item(
    resume_id: UUID, item_type_str: str, item_id: UUID, update_data: dict
):
    """
    Updates a specific item within a resume.
    The request body 'data' should contain the full desired state of the item's
    content (fields, bullets, skills).
    'bullets' should be a list of strings, order determined by list index.
    The backend will diff this against the global item to determine overrides.
    """
    session = db.session
    try:
        item_type_enum = ResumeItemType(item_type_str)
    except ValueError:
        raise ValueError(f"Invalid item_type: {item_type_str}")

    resume_item = (
        session.query(ResumeItem)
        .options(
            joinedload(ResumeItem.resume_bullets),
            joinedload(ResumeItem.overridden_skills),  # Eager load for diffing
        )
        .filter_by(resume_id=resume_id, item_type=item_type_enum, item_id=item_id)
        .first()
    )

    if not resume_item:
        raise ValueError(
            f"ResumeItem not found for resume {resume_id}, type {item_type_str}, item {item_id}"
        )

    global_item = _get_global_item(item_type_enum, item_id)
    if not global_item:
        raise ValueError(f"Global {item_type_str} item with ID {item_id} not found.")

    #  Start Diffing and Updating
    current_field_overrides = dict(
        resume_item.field_overrides.value
        if resume_item.field_overrides is not None
        else {}
    )  # Make a mutable copy
    field_overrides_changed = False

    # Submitted data for simple fields (e.g., title, role, dates, desc_long)
    # This comes from data['content']['data'] in the request payload
    submitted_fields_data = update_data.get("content", {}).get("data", {})

    # Dynamically process fields from submitted_fields_data
    for field_name, submitted_value in submitted_fields_data.items():
        # Skip non-overridable identifiers or fields not present on the global model
        if field_name in ["id", "user_id"] or not hasattr(global_item, field_name):
            if field_name not in ["id", "user_id"]:
                print(
                    f"Warning: Submitted field '{field_name}' not found on global item {global_item.id} of type {item_type_str}. Skipping override."
                )
            continue

        global_value = getattr(global_item, field_name)
        comparable_global_value = global_value

        # Normalize global_value for comparison if it's a date or other special type
        if (
            isinstance(global_value, (datetime.date, datetime.datetime))
            and global_value is not None
        ):
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
        if not current_field_overrides:  # If all overrides were removed
            resume_item.field_overrides = None
        else:
            resume_item.field_overrides = current_field_overrides
        session.add(resume_item)

    #  Handle Bullet Overrides
    # Expect list of strings: ['bullet content 1', 'bullet content 2', ...]
    submitted_bullets_data = update_data.get("content", {}).get("bullets", [])
    global_bullets_query = (
        session.query(BulletPoint)
        .filter_by(parent_id=global_item.id, parent_type=global_item.bullet_parent_type)
        .order_by(BulletPoint.order_index)
    )

    # Check if submitted bullets differ from global bullets
    bullets_differ = _compare_bullet_lists(
        submitted_bullets_data, global_bullets_query.all()
    )

    if bullets_differ:
        # Clear existing overridden bullets for this ResumeItem
        session.query(ResumeBullet).filter_by(
            resume_id=resume_item.resume_id,
            item_type=resume_item.item_type,
            item_id=resume_item.item_id,
        ).delete(synchronize_session=False)
        # Add new overridden bullets
        for idx, bullet_content_str in enumerate(submitted_bullets_data):
            # 'order_index' is the loop index, 'content' is the string itself
            if (
                bullet_content_str is not None
            ):  # Optionally, add more validation like checking for empty strings
                new_bullet = ResumeBullet(
                    resume_id=resume_item.resume_id,
                    item_type=resume_item.item_type,
                    item_id=resume_item.item_id,
                    order_index=idx,
                    content=bullet_content_str,
                )
                session.add(new_bullet)
    else:  # Bullets are same as global, remove any existing overrides
        if (
            session.query(ResumeBullet)
            .filter_by(
                resume_id=resume_item.resume_id,
                item_type=resume_item.item_type,
                item_id=resume_item.item_id,
            )
            .count()
            > 0
        ):
            session.query(ResumeBullet).filter_by(
                resume_id=resume_item.resume_id,
                item_type=resume_item.item_type,
                item_id=resume_item.item_id,
            ).delete(synchronize_session=False)

    #  Handle Skill Overrides
    # Frontend sends list of skill objects: [{'id': 'skill_uuid', 'name': 'Skill Name'}, ...]
    # We only care about the IDs for diffing and storing.
    submitted_skill_ids = [
        skill_data.get("id")
        for skill_data in update_data.get("content", {}).get("skills", [])
        if skill_data.get("id")
    ]

    if hasattr(global_item, "skills"):  # Check if global item type supports skills
        global_skills_query = (
            global_item.skills
        )  # Assuming this is the relationship yielding Skill objects

        skills_differ = _compare_skill_id_lists(
            submitted_skill_ids, global_skills_query
        )

        if skills_differ:
            # Clear existing overridden skills for this ResumeItem
            resume_item.overridden_skills.clear()  # Assuming 'overridden_skills' is the association proxy or relationship
            # Add new overridden skills
            for skill_id_str in submitted_skill_ids:
                try:
                    skill_id_uuid = UUID(skill_id_str)
                    skill = session.query(Skill).get(skill_id_uuid)
                    if skill:
                        resume_item.overridden_skills.append(skill)
                    else:
                        print(
                            f"Warning: Submitted skill ID {skill_id_str} not found. Skipping."
                        )
                except ValueError:
                    print(
                        f"Warning: Invalid UUID format for skill ID {skill_id_str}. Skipping."
                    )
        else:  # Skills are same as global, remove any existing skill overrides
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
    updated_resume_item_entry = (
        session.query(ResumeItem)
        .options(
            joinedload(ResumeItem.resume_bullets),
            joinedload(ResumeItem.overridden_skills),
        )
        .get(resume_item.id)
    )  # Use the primary key of ResumeItem

    if not updated_resume_item_entry:
        # This case should ideally not happen if the item was just committed
        # but as a safeguard:
        raise ValueError(
            f"Failed to re-fetch ResumeItem with ID {resume_item.id} after update."
        )

    return serialize_resume_item_detail(updated_resume_item_entry)


def reorder_resume_items(resume_id, order_data):
    """Reorders items within a resume.
    order_data is expected to be a list of dicts:
    [{'item_type': 'experience', 'item_id': 'uuid', 'order_index': 0}, ...]
    """
    Resume.query.get_or_404(resume_id)  # Validate resume exists
    try:
        for item_order in order_data.get("items", []):
            try:
                item_type_enum = ResumeItemType[item_order["item_type"]]
            except KeyError:
                # Skip or raise error for invalid item_type
                print(
                    f"Warning: Invalid item_type '{item_order['item_type']}' in reorder_resume_items. Skipping."
                )
                continue

            resume_item = ResumeItem.query.filter_by(
                resume_id=resume_id,
                item_type=item_type_enum,
                item_id=item_order["item_id"],
            ).first()

            if resume_item:
                resume_item.order_index = item_order["order_index"]
            else:
                # Optionally, handle items not found (e.g., log warning)
                print(
                    f"Warning: ResumeItem not found for reordering: {item_order}. Skipping."
                )

        db.session.commit()
        return get_resume(resume_id)  # Return the full updated resume
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
            if isinstance(section_data_item, dict) and "id" in section_data_item:
                section_id = section_data_item["id"]
                # Use provided order_index if available, otherwise use list index
                order_index = section_data_item.get("order_index", index)
                new_order_map[str(section_id)] = order_index
            elif isinstance(
                section_data_item, (str, UUID)
            ):  # If it's just a list of IDs
                new_order_map[str(section_data_item)] = index
            else:
                raise ValueError("Invalid format for sections_order_data item.")

        updated_sections_count = 0
        for section in resume.sections:  # Assuming resume.sections is the relationship
            if str(section.id) in new_order_map:
                section.order_index = new_order_map[str(section.id)]
                updated_sections_count += 1

        if updated_sections_count == 0 and len(sections_order_data) > 0:
            # TODO
            # This might mean none of the provided section IDs matched existing sections.
            # Depending on desired behavior, this could be an error or just a no-op.
            pass  # Or raise ValueError("No matching sections found to reorder.")

        db.session.commit()
        # Reload or re-fetch resume to get sections in updated order for serialization
        db.session.refresh(resume)
        # order should be handled by the Model relationship with order_by
        return serialize_resume(resume, include_details=True)

    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Database error updating resume sections order: {str(e)}")
    except ValueError as e:  # Catch specific ValueErrors from logic above
        db.session.rollback()
        raise e


#  Helper functions for diffing


def _compare_bullet_lists(
    submitted_bullet_strings: list[str], global_bullets_query_result: list[BulletPoint]
):
    """
    Compares a list of submitted bullet content (strings) with a list of global BulletPoint objects.
    Returns True if they are different, False otherwise.
    Order is determined by list index for submitted_bullet_strings.
    Assumes global_bullets_query_result is sorted by order_index.
    """
    # global_bullets_list is already sorted by order_index from the query
    global_bullets_list = global_bullets_query_result

    if len(submitted_bullet_strings) != len(global_bullets_list):
        return True
    for i, submitted_content_str in enumerate(submitted_bullet_strings):
        global_bullet = global_bullets_list[i]
        # Compare content. Order is implicitly compared by list position.
        if submitted_content_str != global_bullet.content:
            return True
    return False


def _compare_skill_id_lists(submitted_skill_ids: list, global_skills_query):
    """
    Compares a list of submitted skill IDs with a query of global Skill objects.
    Returns True if they are different, False otherwise.
    """
    global_skill_id_set = {str(skill.id) for skill in global_skills_query}
    submitted_skill_id_set = set(
        map(str, submitted_skill_ids)
    )  # Ensure submitted IDs are strings

    return global_skill_id_set != submitted_skill_id_set


# ---- ResumeSection specific serialization ----
def serialize_resume_section(section: ResumeSection, include_items: bool = False):
    """Serializes a ResumeSection, optionally including its items."""
    data = {
        "resume_id": str(section.resume_id),
        "section_type": section.section_type.value,
        "title": section.title,
        "order_index": section.order_index,
        "items": [],
    }
    if include_items:
        # section.items will be ordered by ResumeItem.order_index due to model relationship's order_by
        for item in section.items:
            item_detail = serialize_resume_item_detail(item)
            if item_detail:
                data["items"].append(item_detail)
    return data


# ---- ResumeSection CRUD ----


def _ensure_section_exists(
    session: SQLAlchemySession,
    resume_id: UUID,
    section_type: ResumeItemType,
    title: Optional[str] = None,
    order_index: Optional[int] = None,
) -> ResumeSection:
    """
    Finds an existing section or creates it if it doesn't exist.
    If creating, title and order_index are required.
    """
    section = (
        session.query(ResumeSection)
        .filter_by(resume_id=resume_id, section_type=section_type)
        .first()
    )

    if not section:
        if title is None:  # Default title if not provided for auto-creation
            title = section_type.value.replace("_", " ").capitalize()

        if order_index is None:  # Determine next order_index if not provided
            max_order = (
                session.query(func.max(ResumeSection.order_index))
                .filter_by(resume_id=resume_id)
                .scalar()
            )
            order_index = (max_order + 1) if max_order is not None else 0

        section = ResumeSection(
            resume_id=resume_id,
            section_type=section_type,
            title=title,
            order_index=order_index,
        )
        session.add(section)
        # Flush to get the section in the session for immediate use if needed by caller.
        session.flush()
    elif (
        title is not None and section.title != title
    ):  # Optionally update title if provided and different
        section.title = title
        session.flush()

    return section


def create_resume_section(resume_id: UUID, data: dict):
    """
    Explicitly creates a new section in a resume or updates its title if it exists.
    `data` should contain `section_type` (string) and `title` (string).
    `order_index` is optional; if not provided, it's appended.
    """
    resume = Resume.query.get_or_404(resume_id)

    section_type_str = data.get("section_type")
    title = data.get("title")
    order_index = data.get("order_index")  # Optional for explicit creation

    if not section_type_str or not title:
        raise ValueError("Missing 'section_type' or 'title' for the section.")

    try:
        section_type_enum = ResumeItemType[section_type_str]
    except KeyError:
        raise ValueError(
            f"Invalid section_type: {section_type_str}. Must be one of {', '.join([e.value for e in ResumeItemType])}."
        )

    session = db.session
    try:
        # Check if section of this type already exists
        existing_section = (
            session.query(ResumeSection)
            .filter_by(resume_id=resume.id, section_type=section_type_enum)
            .first()
        )

        if existing_section:
            # If it exists, update its title and optionally order_index
            existing_section.title = title
            if order_index is not None:
                existing_section.order_index = order_index
            section_to_serialize = existing_section
        else:
            # If it doesn't exist, create it
            if order_index is None:
                max_order = (
                    session.query(func.max(ResumeSection.order_index))
                    .filter_by(resume_id=resume.id)
                    .scalar()
                )
                order_index = (max_order + 1) if max_order is not None else 0

            new_section = ResumeSection(
                resume_id=resume.id,
                section_type=section_type_enum,
                title=title,
                order_index=order_index,
            )
            session.add(new_section)
            section_to_serialize = new_section

        session.commit()
        session.refresh(section_to_serialize)
        return serialize_resume_section(section_to_serialize, include_items=False)
    except SQLAlchemyError as e:
        session.rollback()
        raise ValueError(f"Error creating/updating resume section: {str(e)}")


def delete_resume_section(resume_id: UUID, section_type_str: str):
    """Removes a section (identified by its type) and its items from a resume."""
    try:
        section_type_enum = ResumeItemType[section_type_str]
    except KeyError:
        raise ValueError(f"Invalid section_type: {section_type_str}")

    section = ResumeSection.query.filter_by(
        resume_id=resume_id, section_type=section_type_enum
    ).first_or_404(
        description=f"Section of type '{section_type_str}' not found for this resume."
    )

    try:
        db.session.delete(
            section
        )  # Associated ResumeItems should be cascade deleted due to FK
        db.session.commit()
        return {"message": f"Resume section '{section_type_str}' deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(
            f"Error deleting resume section '{section_type_str}': {str(e)}"
        )


# ---- ResumeItem specific functions ----


def add_item_to_resume_section(
    resume_id: UUID,
    target_section_type_str: str,  # e.g., "project", "experience" - this is the section it goes into
    global_item_id: UUID,  # ID of the Education, Experience, Project object
    # item_type_of_global_item_str: str, # Type of the global item being added, e.g. "project"
    data: Optional[dict] = None,
):
    """
    Adds a global item to a specific section of a resume.
    The section is identified by target_section_type_str.
    If the section doesn't exist, it's created.
    The item_type of the ResumeItem created will match target_section_type_str.
    """
    data = data or {}
    session = db.session
    resume = session.query(Resume).get(resume_id)
    if not resume:
        raise ValueError(f"Resume with ID {resume_id} not found.")

    try:
        # This is the type of the section the item will belong to,
        # and also the item_type for the ResumeItem entry.
        section_type_enum = ResumeItemType[target_section_type_str]
    except KeyError:
        raise ValueError(f"Invalid target_section_type: {target_section_type_str}")

    # Validate the global item exists and its type matches the target section type
    # (This assumes a "project" global item goes into a "project" section type, etc.)
    global_item = _get_global_item(
        section_type_enum, global_item_id
    )  # _get_global_item uses section_type_enum to find the correct global table
    if not global_item:
        raise ValueError(
            f"Global item of type {target_section_type_str} with ID {global_item_id} not found."
        )

    # Ensure the section exists, or create it
    # The title for auto-created section can be default or passed in data
    section_title_for_creation = data.get(
        "section_title", section_type_enum.value.replace("_", " ").capitalize()
    )
    target_section = _ensure_section_exists(
        session, resume_id, section_type_enum, title=section_title_for_creation
    )
    # _ensure_section_exists will flush if it creates/updates.

    # Check if item already exists in the section (ResumeItem PK is resume_id, item_type, item_id)
    existing_resume_item = (
        session.query(ResumeItem)
        .filter_by(
            resume_id=resume_id,
            item_type=section_type_enum,  # This is the section type
            item_id=global_item_id,
        )
        .first()
    )

    if existing_resume_item:
        raise ValueError(
            f"Item ID {global_item_id} (type {section_type_enum.value}) already exists in section '{target_section.title}'."
        )

    # Determine order_index for the new item within its section
    order_index = data.get("order_index")
    if order_index is None:
        max_order = (
            session.query(func.max(ResumeItem.order_index))
            .filter_by(
                resume_id=resume_id,
                item_type=section_type_enum,  # Order within this specific section type
            )
            .scalar()
        )
        order_index = (max_order + 1) if max_order is not None else 0

    new_resume_item = ResumeItem(
        resume_id=resume_id,
        item_type=section_type_enum,  # Links to ResumeSection.section_type
        item_id=global_item_id,
        order_index=order_index,
        field_overrides=data.get("field_overrides"),  # Pass overrides if provided
    )

    try:
        session.add(new_resume_item)
        session.commit()
        # Refresh to get all attributes, especially if defaults are set by DB
        # and to ensure relationships are fresh if accessed immediately.
        session.refresh(new_resume_item)
        return serialize_resume_item_detail(new_resume_item)
    except SQLAlchemyError as e:
        session.rollback()
        # A more specific error might be useful, e.g., if FK constraint fails
        raise ValueError(f"Error adding item to resume section: {str(e)}")
