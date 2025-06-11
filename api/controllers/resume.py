from sqlalchemy import select
from sqlalchemy.orm import selectinload

from flask import current_app

from models.resume import Resume, ResumeSection, ResumeItem, ResumeItemType
from models.user import User
from models.template import Template

from datetime import datetime, timezone

from models.resume import SECTION_TYPE_TO_DISPLAY_NAME_MAPPING

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
        if date_string.endswith("Z"):
            date_string = date_string[:-1] + "+00:00"

        dt_object = datetime.fromisoformat(date_string)

        # Ensure the datetime object is timezone-aware, defaulting to UTC if naive
        if dt_object.tzinfo is None:
            return dt_object.replace(tzinfo=timezone.utc)
        return dt_object.astimezone(
            timezone.utc
        )  # Convert to UTC if it has other timezone
    except ValueError:
        # Log an error or handle appropriately if parsing fails
        print(
            f"Warning: Could not parse date string: {date_string}"
        )  # Or use proper logging
        return None


# TODO: Implement other controller functions:
def _parse_item_data(item_payload: dict, user_id: int) -> dict | None:
    """
    Parses and validates item payload data. Returns a dictionary of parsed data or None if validation fails.
    """
    required_fields = ["title", "organization", "start_date", "location", "description"]
    for field in required_fields:
        if field not in item_payload or item_payload[field] is None:
            print(f"Warning: Missing required field {field} in item payload.")
            return None

    parsed_data = {
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


def _find_or_create_item(
    item_payload: dict, user_id: int, section_id: int, display_order: int, db_session
) -> ResumeItem | None:
    """
    Finds an existing ResumeItem by ID or creates a new one for the given section.
    It ensures the item belongs to the current user and section if an ID is provided.
    """
    item_id = item_payload.get("id")
    item = None

    if item_id is not None:
        try:
            item_id = int(item_id)
            stmt = select(ResumeItem).where(
                ResumeItem.id == item_id,
                ResumeItem.user_id == user_id,
                ResumeItem.section_id
                == section_id,  # Item must belong to the section being processed
            )
            item = db_session.execute(stmt).scalar_one_or_none()
            # If item is not found, we fall through and create a new one below.
        except (ValueError, TypeError):
            # If item_id is not a valid integer (e.g., a client-side UUID), treat as a new item.
            item = None
            print(
                f"Warning: Invalid item_id format: {item_payload.get('id')}. Treating as new item."
            )

    parsed_data = _parse_item_data(item_payload, user_id)
    if not parsed_data:
        return None

    if item:  # Existing item found, update it
        for key, value in parsed_data.items():
            setattr(item, key, value)
        item.display_order = display_order  # Always update display order
    else:  # New item
        item = ResumeItem()
        for key, value in parsed_data.items():
            setattr(item, key, value)
        item.user_id = user_id
        item.section_id = section_id
        item.display_order = display_order
        db_session.add(item)
    return item


def _find_or_create_section(
    section_payload: dict, resume_id: int, user_id: int, display_order: int, db_session
) -> ResumeSection | None:
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
                ResumeSection.resume_id == resume_id,
            )
            section = db_session.execute(stmt).scalar_one_or_none()
            # If section is not found, we fall through to create a new one below.
        except (ValueError, TypeError):
            # If section_id is not a valid int, treat as a new section.
            section = None
            print(
                f"Warning: Invalid section_id format: {section_payload.get('id')}. Treating as new section."
            )

    section_type_input = section_payload.get("type") or section_payload.get(
        "section_type"
    )
    try:
        section_type_val = ResumeItemType(
            str(section_type_input).lower()
        )  # lower in case frontend sends it with capitalized letters
    except ValueError:
        print(f"Warning: Invalid section_type: {section_type_input}")
        return None

    name = section_payload.get("name")
    if not name:
        print("Warning: Missing name for section.")
        return None

    if section:  # Existing section, update it
        section.name = name
        section.section_type = section_type_val
        section.display_order = display_order
    else:  # New section
        section = ResumeSection()
        section.user_id = user_id
        section.resume_id = resume_id
        section.name = name
        section.section_type = section_type_val
        section.display_order = display_order
        db_session.add(section)
        db_session.flush()  # Ensure ID is available for item processing
    return section


def _update_section_items(
    section_db: ResumeSection, items_payload: list[dict], user_id: int, db_session
):
    """
    Synchronizes the items of a given section with the payload using a one-to-many relationship.
    Creates, updates, or deletes items as needed. Manages item order within the section.
    """
    # By replacing the collection, SQLAlchemy's delete-orphan cascade handles deletions.
    updated_items_collection = []
    for item_idx, item_data_payload in enumerate(items_payload):
        # We now pass the section_id and display_order directly
        item_db = _find_or_create_item(
            item_data_payload, user_id, section_db.id, item_idx, db_session
        )
        if not item_db:
            print(
                f"Skipping item due to creation/find failure: {item_data_payload.get('title')}"
            )
            # Potentially raise an error here to abort the transaction
            continue
        updated_items_collection.append(item_db)

    # This is the key change: assigning the new list to the relationship collection.
    # SQLAlchemy will automatically detect which items are new (INSERT), which are removed (DELETE),
    # and which are existing (and will be updated by the logic in _find_or_create_item).
    section_db.items = updated_items_collection


def process_resume_update(resume_db: Resume, payload: dict, db_session):
    """
    Main controller function to process updates to a resume, including its sections and items.
    Updates are delegated to the user or resume object as appropriate.
    """
    # Validation Checks
    sections_payload = payload.get("sections", [])

    # Ensure all section types are present and there are no extras
    payload_section_types = {s.get("section_type") for s in sections_payload}
    all_enum_types = {e.value for e in ResumeItemType}

    if payload_section_types != all_enum_types:
        missing = all_enum_types - payload_section_types
        extra = payload_section_types - all_enum_types
        error_msg = "Resume must have exactly one of each section type."
        if missing:
            error_msg += f" Missing: {', '.join(missing)}."
        if extra:
            error_msg += f" Extra: {', '.join(extra)}."
        raise ValueError(error_msg)

    # Ensure no section is empty
    for section_data in sections_payload:
        if not section_data.get("items"):
            section_name = section_data.get("name", "Unnamed")
            raise ValueError(
                f"Section '{section_name}' cannot be empty. Please add at least one item."
            )

    # Update User fields via the relationship
    user_to_update = resume_db.user
    user_to_update.name = payload.get("name", user_to_update.name)
    user_to_update.phone = payload.get("phone", user_to_update.phone)
    user_to_update.email = payload.get("email", user_to_update.email)
    user_to_update.linkedin = payload.get("linkedin", user_to_update.linkedin)
    user_to_update.github = payload.get("github", user_to_update.github)
    user_to_update.website = payload.get("website", user_to_update.website)

    # Update Resume-specific fields
    resume_db.resume_name = payload.get("resume_name", resume_db.resume_name)
    if "template_id" in payload:
        resume_db.template_id = payload["template_id"]

    # Process Sections
    sections_payload = payload.get("sections", [])
    user_id = user_to_update.id  # Keep user_id for nested calls for simplicity

    # Get current sections from DB for this resume to find orphans later
    current_db_sections_stmt = select(ResumeSection.id).where(
        ResumeSection.resume_id == resume_db.id
    )
    current_db_section_ids = {
        s_id for (s_id,) in db_session.execute(current_db_sections_stmt).all()
    }
    processed_section_ids_in_payload = set()

    for section_idx, section_data_payload in enumerate(sections_payload):
        section_db = _find_or_create_section(
            section_data_payload, resume_db.id, user_id, section_idx, db_session
        )
        if not section_db:
            print(
                f"Skipping section due to creation/find failure: {section_data_payload.get('name')}"
            )
            continue  # Skip processing this section if it failed

        processed_section_ids_in_payload.add(section_db.id)

        items_payload_for_section = section_data_payload.get("items", [])
        _update_section_items(
            section_db, items_payload_for_section, user_id, db_session
        )

    # Delete Orphaned Sections (sections in DB but not in payload for this resume)
    section_ids_to_delete = current_db_section_ids - processed_section_ids_in_payload
    for sec_id_to_delete in section_ids_to_delete:
        section_to_delete_stmt = select(ResumeSection).where(
            ResumeSection.id == sec_id_to_delete,
            ResumeSection.user_id == user_id,
            ResumeSection.resume_id == resume_db.id,
        )
        section_to_delete = db_session.execute(
            section_to_delete_stmt
        ).scalar_one_or_none()
        if section_to_delete:
            db_session.delete(
                section_to_delete
            )  # Cascading delete should handle its associations
            print(
                f"Deleting orphaned section_id {sec_id_to_delete} from resume_id {resume_db.id}"
            )

    # Save changes for resume scalars, new/updated sections, items, associations
    # The db_session.commit() will be handled in the view function after this returns.
    return resume_db


def create_new_resume(user: User, db_session) -> Resume:
    """
    Creates a new resume, fully populated with default sections and a default item for each section.
    """
    # Find a default template

    default_template = db_session.execute(
        select(Template).limit(1)
    ).scalar_one_or_none()
    if not default_template:
        # TODO: for future custom template support
        # Create a default template
        default_template = Template()
        default_template.name = "Default Template"
        default_template.uri = ""
        db_session.add(default_template)
        db_session.flush()
        default_template = db_session.execute(
            select(Template).limit(1)
        ).scalar_one_or_none()
        
        current_app.logger.info("No templates found in the system. Creating a default template.")
        # raise Exception("No templates found in the system. Cannot create a resume.")

    # Generate a unique default name
    base_name = "Untitled Resume"
    existing_names_stmt = select(Resume.resume_name).where(
        Resume.user_id == user.id, Resume.resume_name.like(f"{base_name}%")
    )
    existing_names = db_session.execute(existing_names_stmt).scalars().all()
    new_name = base_name
    counter = 1
    while new_name in existing_names:
        counter += 1
        new_name = f"{base_name} ({counter})"

    # Create the resume object
    new_resume = Resume()
    new_resume.user_id = user.id
    new_resume.resume_name = new_name
    new_resume.template_id = default_template.id
    db_session.add(new_resume)
    db_session.flush()  # Flush to get the new_resume.id

    # Create a default section and item for each type

    ordered_section_types = [
        ResumeItemType.education,
        ResumeItemType.experience,
        ResumeItemType.project,
        ResumeItemType.skill,
    ]

    for i, section_type in enumerate(ordered_section_types):
        section_name = SECTION_TYPE_TO_DISPLAY_NAME_MAPPING[section_type]
        new_section = ResumeSection()
        new_section.user_id = user.id
        new_section.resume_id = new_resume.id
        new_section.name = section_name
        new_section.section_type = section_type
        new_section.display_order = i
        db_session.add(new_section)
        db_session.flush()  # Flush to get the new_section.id

        if section_type == ResumeItemType.skill:
            new_item = ResumeItem()
            new_item.user_id = user.id
            new_item.section_id = new_section.id
            new_item.title = "Skill Category"
            new_item.organization = ""
            new_item.start_date = datetime.now()
            new_item.end_date = None
            new_item.location = ""
            new_item.description = "Resume-building, problem-solving, etc"
        elif section_type == ResumeItemType.project:
            new_item = ResumeItem()
            new_item.user_id = user.id
            new_item.section_id = new_section.id
            new_item.title = "Project Name"
            new_item.organization = ""
            new_item.start_date = datetime.now()
            new_item.end_date = None
            new_item.location = ""
            new_item.description = "Project description"
        elif section_type == ResumeItemType.experience:
            new_item = ResumeItem()
            new_item.user_id = user.id
            new_item.section_id = new_section.id
            new_item.title = "Job Title"
            new_item.organization = "Company Name"
            new_item.start_date = datetime.now()
            new_item.end_date = None
            new_item.location = ""
            new_item.description = "Job description"
        elif section_type == ResumeItemType.education:
            new_item = ResumeItem()
            new_item.user_id = user.id
            new_item.section_id = new_section.id
            new_item.title = "Degree"
            new_item.organization = "University Name"
            new_item.start_date = datetime.now()
            new_item.end_date = None
            new_item.location = ""
            new_item.description = "Degree description"
        else:
            raise ValueError(f"Invalid section type: {section_type}")

        db_session.add(new_item)

    return new_resume


def get_full_resume(resume_id: int, user: User, db_session) -> Resume | None:
    """
    Fetches a single resume with all its sections and items eagerly loaded.
    Ensures the resume belongs to the specified user by checking the relationship.
    """
    stmt = (
        select(Resume)
        .where(Resume.id == resume_id, Resume.user == user)
        .options(selectinload(Resume.sections).selectinload(ResumeSection.items))
    )
    return db_session.execute(stmt).scalar_one_or_none()
