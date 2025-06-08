from flask_login import current_user

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from models.resume import Resume, ResumeSection, ResumeItem, ResumeItemType
from models.user import User
from db import db

from datetime import datetime, timezone


# TODO(bliutech): refactor core logic from views/resume.py into here

def parse_iso_date_string(date_string: str | None) -> datetime | None:
    """
    Parses an ISO 8601 date string into a timezone-aware datetime object (UTC).
    Returns None if the input is None or empty, or if parsing fails.
    Handles common ISO 8601 formats, including those with 'Z' for UTC.
    """
    if not date_string:
        return None
    try:
        # Replace 'Z' with '+00:00' for broader compatibility with fromisoformat
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        
        dt_object = datetime.fromisoformat(date_string)
        
        # Ensure the datetime object is timezone-aware, defaulting to UTC if naive
        if dt_object.tzinfo is None:
            return dt_object.replace(tzinfo=timezone.utc)
        return dt_object.astimezone(timezone.utc) # Convert to UTC if it has other timezone
    except ValueError:
        # Log an error or handle appropriately if parsing fails
        print(f"Warning: Could not parse date string: {date_string}") # Or use proper logging
        return None


# TODO: Implement other controller functions:
def _parse_item_data(item_payload: dict, user_id: int) -> dict | None:
    """
    Parses and validates item payload data. Returns a dictionary of parsed data or None if validation fails.
    """
    required_fields = ["item_type", "title", "organization", "start_date", "location", "description"]
    for field in required_fields:
        if field not in item_payload or item_payload[field] is None:
            print(f"Warning: Missing required field {field} in item payload.")
            return None

    try:
        item_type_value = item_payload["item_type"]
        item_type = ResumeItemType(str(item_type_value))
    except ValueError:
        print(f"Warning: Invalid item_type: {item_payload.get('item_type')}")
        return None

    parsed_data = {
        "item_type": item_type,
        "title": str(item_payload["title"]),
        "organization": str(item_payload["organization"]),
        "start_date": parse_iso_date_string(item_payload["start_date"]),
        "end_date": parse_iso_date_string(item_payload.get("end_date")),
        "location": str(item_payload["location"]),
        "description": str(item_payload["description"]),
    }

    if not parsed_data["start_date"]:
         print(f"Warning: Invalid start_date format: {item_payload['start_date']}")
         return None

    # If end_date was provided but couldn't be parsed, it would be None here, which is acceptable for nullable field.
    return parsed_data

def _find_or_create_item(item_payload: dict, user_id: int, section_id: int, display_order: int, db_session) -> ResumeItem | None:
    """
    Finds an existing ResumeItem by ID or creates a new one for the given section.
    It ensures the item belongs to the current user and section if an ID is provided.
    """
    item_id = item_payload.get("id")
    item = None

    # Only lookup if ID is an int from DB. Client-side IDs are strings.
    if isinstance(item_id, int):
        stmt = select(ResumeItem).where(
            ResumeItem.id == item_id, 
            ResumeItem.user_id == user_id,
            ResumeItem.section_id == section_id # Item must belong to the section being processed
        )
        item = db_session.execute(stmt).scalar_one_or_none()
        if not item:
            print(f"Warning: ResumeItem with id {item_id} not found for user {user_id} and section {section_id}.")
            return None

    parsed_data = _parse_item_data(item_payload, user_id)
    if not parsed_data:
        return None

    if item: # Existing item found, update it
        for key, value in parsed_data.items():
            setattr(item, key, value)
        item.display_order = display_order # Always update display order
    else: # New item
        item = ResumeItem()
        for key, value in parsed_data.items():
            setattr(item, key, value)
        item.user_id = user_id
        item.section_id = section_id
        item.display_order = display_order
        db_session.add(item)
    return item

def _find_or_create_section(section_payload: dict, resume_id: int, user_id: int, display_order: int, db_session) -> ResumeSection | None:
    """
    Finds an existing ResumeSection by ID or creates a new one for the given resume and user.
    Updates display_order for both existing and new sections.
    """
    section_id = section_payload.get("id")
    section = None

    # Only lookup if ID is an int from DB. Client-side IDs are strings.
    if isinstance(section_id, int):
        stmt = select(ResumeSection).where(
            ResumeSection.id == section_id, 
            ResumeSection.user_id == user_id, 
            ResumeSection.resume_id == resume_id
        )
        section = db_session.execute(stmt).scalar_one_or_none()
        if not section:
            print(f"Warning: ResumeSection with id {section_id} not found for user {user_id} and resume {resume_id}.")
            # As with items, don't create if an invalid ID was passed.
            return None

    section_type_input = section_payload.get("type") or section_payload.get("section_type")
    try:
        section_type_val = ResumeItemType(str(section_type_input))
    except ValueError:
        print(f"Warning: Invalid section_type: {section_type_input}")
        return None

    name = section_payload.get("name")
    if not name:
        print(f"Warning: Missing name for section.")
        return None

    if section: # Existing section, update it
        section.name = name
        section.section_type = section_type_val
        section.display_order = display_order
    else: # New section
        section = ResumeSection()
        section.user_id = user_id
        section.resume_id = resume_id
        section.name = name
        section.section_type = section_type_val
        section.display_order = display_order
        db_session.add(section)
        db_session.flush() # Ensure ID is available for item processing
    return section

def _update_section_items(section_db: ResumeSection, items_payload: list[dict], user_id: int, db_session):
    """
    Synchronizes the items of a given section with the payload using a one-to-many relationship.
    Creates, updates, or deletes items as needed. Manages item order within the section.
    """
    # By replacing the collection, SQLAlchemy's delete-orphan cascade handles deletions.
    updated_items_collection = []
    for item_idx, item_data_payload in enumerate(items_payload):
        # We now pass the section_id and display_order directly
        item_db = _find_or_create_item(item_data_payload, user_id, section_db.id, item_idx, db_session)
        if not item_db:
            print(f"Skipping item due to creation/find failure: {item_data_payload.get('title')}")
            # Potentially raise an error here to abort the transaction
            continue
        updated_items_collection.append(item_db)

    # This is the key change: assigning the new list to the relationship collection.
    # SQLAlchemy will automatically detect which items are new (INSERT), which are removed (DELETE),
    # and which are existing (and will be updated by the logic in _find_or_create_item).
    section_db.items = updated_items_collection

def process_resume_update(resume_db: Resume, payload: dict, user_id: int, db_session):
    """
    Main controller function to process updates to a resume, including its sections and items.
    """
    # Update Resume scalar fields
    resume_db.name = payload.get("name", resume_db.name)
    resume_db.resume_name = payload.get("resume_name", resume_db.resume_name)
    resume_db.phone = payload.get("phone", resume_db.phone)
    resume_db.email = payload.get("email", resume_db.email)
    resume_db.linkedin = payload.get("linkedin", resume_db.linkedin)
    resume_db.github = payload.get("github", resume_db.github)
    resume_db.website = payload.get("website", resume_db.website)
    if "template_id" in payload:
        resume_db.template_id = payload["template_id"]

    # Process Sections
    sections_payload = payload.get("sections", [])
    
    # Get current sections from DB for this resume to find orphans later
    current_db_sections_stmt = select(ResumeSection.id).where(ResumeSection.resume_id == resume_db.id)
    current_db_section_ids = {s_id for s_id, in db_session.execute(current_db_sections_stmt).all()}
    processed_section_ids_in_payload = set()

    for section_idx, section_data_payload in enumerate(sections_payload):
        section_db = _find_or_create_section(section_data_payload, resume_db.id, user_id, section_idx, db_session)
        if not section_db:
            print(f"Skipping section due to creation/find failure: {section_data_payload.get('name')}")
            continue # Skip processing this section if it failed
        
        processed_section_ids_in_payload.add(section_db.id)
        
        items_payload_for_section = section_data_payload.get("items", [])
        _update_section_items(section_db, items_payload_for_section, user_id, db_session)

    # Delete Orphaned Sections (sections in DB but not in payload for this resume)
    section_ids_to_delete = current_db_section_ids - processed_section_ids_in_payload
    for sec_id_to_delete in section_ids_to_delete:
        section_to_delete_stmt = select(ResumeSection).where(ResumeSection.id == sec_id_to_delete, ResumeSection.user_id == user_id, ResumeSection.resume_id == resume_db.id)
        section_to_delete = db_session.execute(section_to_delete_stmt).scalar_one_or_none()
        if section_to_delete:
            db_session.delete(section_to_delete) # Cascading delete should handle its associations
            print(f"Deleting orphaned section_id {sec_id_to_delete} from resume_id {resume_db.id}")
    
    # Save changes for resume scalars, new/updated sections, items, associations
    # The db_session.commit() will be handled in the view function after this returns.
    return resume_db

def get_full_resume(resume_id: int, user_id: int, db_session) -> Resume | None:
    """
    Fetches a single resume with all its sections and items eagerly loaded.
    Ensures the resume belongs to the specified user.
    """
    stmt = (
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == user_id)
        .options(
            selectinload(Resume.sections).selectinload(ResumeSection.items)
        )
    )
    return db_session.execute(stmt).scalar_one_or_none()
