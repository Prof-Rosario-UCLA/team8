from flask_login import current_user

from sqlalchemy import select, func

from models.resume import Resume, ResumeSection, ResumeItem, ResumeAssociation, ResumeItemType
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
        if isinstance(item_type_value, ResumeItemType): # Already an enum instance
             item_type = item_type_value
        else: # Assume it's a string, try to convert
            item_type = ResumeItemType(str(item_type_value)) # Validate against Enum
    except ValueError:
        print(f"Warning: Invalid item_type: {item_payload.get('item_type')}")
        return None

    parsed_data = {
        "user_id": user_id,
        "item_type": item_type,
        "title": str(item_payload["title"]),
        "organization": str(item_payload["organization"]),
        "start_date": parse_iso_date_string(item_payload["start_date"]),
        "end_date": parse_iso_date_string(item_payload.get("end_date")), # Optional
        "location": str(item_payload["location"]),
        "description": str(item_payload["description"]),
    }

    if parsed_data["start_date"] is None and "start_date" in required_fields:
         print(f"Warning: Invalid start_date format: {item_payload['start_date']}")
         return None

    # If end_date was provided but couldn't be parsed, it would be None here, which is acceptable for nullable field.
    return parsed_data

def _find_or_create_item(item_payload: dict, user_id: int, db_session) -> ResumeItem | None:
    """
    Finds an existing ResumeItem by ID (if provided and valid) or creates a new one.
    Ensures the item belongs to the current user if an ID is provided.
    """
    item_id = item_payload.get("id")
    item = None

    if item_id is not None:
        try:
            item_id = int(item_id)
            stmt = select(ResumeItem).where(ResumeItem.id == item_id, ResumeItem.user_id == user_id)
            item = db_session.execute(stmt).scalar_one_or_none()
            if not item:
                print(f"Warning: ResumeItem with id {item_id} not found for user {user_id} or ID is invalid.")
                # Do not create a new one if an invalid ID was passed; frontend should send no ID for new items.
                return None 
        except ValueError:
            print(f"Warning: Invalid item_id format: {item_payload.get('id')}. Expected integer or None.")
            return None # Invalid ID format

    parsed_data = _parse_item_data(item_payload, user_id)
    if not parsed_data:
        return None # Parsing/validation failed

    if item: # Existing item found, update it
        for key, value in parsed_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
    else: # No valid ID provided or item not found by ID, create new
        item = ResumeItem()
        for key, value in parsed_data.items(): # Assign attributes from parsed_data
            setattr(item, key, value)
        db_session.add(item)
        # Flush is important here if this item needs to be associated immediately
        # and its ID is required by the caller before main commit.
        db_session.flush() 
    return item

def _find_or_create_section(section_payload: dict, resume_id: int, user_id: int, display_order: int, db_session) -> ResumeSection | None:
    """
    Finds an existing ResumeSection by ID or creates a new one for the given resume and user.
    Updates display_order for both existing and new sections.
    """
    section_id = section_payload.get("id")
    section = None

    if section_id is not None:
        try:
            section_id = int(section_id)
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
        except ValueError:
            print(f"Warning: Invalid section_id format: {section_payload.get('id')}. Expected integer or None.")
            return None

    section_type_input = section_payload.get("type") or section_payload.get("section_type")
    try:
        if isinstance(section_type_input, ResumeItemType):
            section_type_val = section_type_input
        else:
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
    Synchronizes the items of a given section with the payload.
    Creates, updates, or deletes items and their associations as needed.
    Manages item order within the section.
    """
    existing_associations_stmt = select(ResumeAssociation).where(
        ResumeAssociation.section_id == section_db.id,
        ResumeAssociation.user_id == user_id
    )
    # Map of item_id to its current association object for quick lookup
    current_associations_map = {assoc.item_id: assoc for assoc in db_session.execute(existing_associations_stmt).scalars().all()}
    processed_item_ids_in_payload = set()

    for item_idx, item_data_payload in enumerate(items_payload):
        item_db = _find_or_create_item(item_data_payload, user_id, db_session)
        if not item_db:
            print(f"Skipping item due to creation/find failure: {item_data_payload.get('title')}")
            continue # Skip this item if it couldn't be processed
        
        processed_item_ids_in_payload.add(item_db.id)

        if item_db.id in current_associations_map: # Item is already associated with this section
            assoc = current_associations_map[item_db.id]
            assoc.display_order = item_idx # Update display order
        else: # New association needed for this item and section
            new_assoc = ResumeAssociation()
            new_assoc.user_id = user_id
            new_assoc.section_id = section_db.id
            new_assoc.item_id = item_db.id
            new_assoc.display_order = item_idx
            db_session.add(new_assoc)
            # No flush needed here, will be flushed with section or resume save.

    # Unlink items: Remove associations for items that were previously in the section but not in the current payload
    item_ids_to_unlink = set(current_associations_map.keys()) - processed_item_ids_in_payload
    for item_id_to_unlink in item_ids_to_unlink:
        assoc_to_delete = current_associations_map[item_id_to_unlink]
        db_session.delete(assoc_to_delete)
        print(f"Unlinking item_id {item_id_to_unlink} from section_id {section_db.id}")

    # Note: This function does not delete ResumeItem objects themselves if they are unlinked.
    # Deletion of orphaned ResumeItems (not linked to ANY section) could be a separate cleanup process if desired.

def process_resume_update(resume_db: Resume, payload: dict, user_id: int, db_session):
    """
    Main controller function to process updates to a resume, including its sections and items.
    """
    # 1. Update Resume scalar fields
    resume_db.name = payload.get("name", resume_db.name)
    resume_db.resume_name = payload.get("resume_name", resume_db.resume_name)
    resume_db.phone = payload.get("phone", resume_db.phone)
    resume_db.email = payload.get("email", resume_db.email)
    resume_db.linkedin = payload.get("linkedin", resume_db.linkedin)
    resume_db.github = payload.get("github", resume_db.github)
    resume_db.website = payload.get("website", resume_db.website)
    if "template_id" in payload:
        resume_db.template_id = payload["template_id"]

    # 2. Process Sections
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

    # 3. Delete Orphaned Sections (sections in DB but not in payload for this resume)
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
