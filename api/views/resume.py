from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_, func, delete
from sqlalchemy.orm import selectinload

from models.user import User
from models.resume import Resume, ResumeSection, ResumeItem
from models.template import Template
from flask_login import login_required, current_user

from db import db
from controllers.resume import process_resume_update, get_full_resume

resume_views = Blueprint("resume_views", __name__, url_prefix="/resume")

# ==================== Resume Routes ====================


@resume_views.get("/all")
@login_required
def get_all_resumes():
    """
    Return all resumes belonging to a user.
    """
    stmt = select(Resume).where(Resume.user_id == current_user.id)
    result = db.session.execute(stmt)
    result = result.scalars().all()
    result = [r.json() for r in result]

    return jsonify({"resumes": result})


@resume_views.get("/<int:id>")
@login_required
def get_resume(id: int):
    """
    Return a resume belonging to the current user
    with a given resume id, using the controller to fetch it.
    """
    resume = get_full_resume(id, current_user.id, db.session)
    if resume:
        return resume.json()
    return jsonify({"error": "Resume not found"}), 404


@resume_views.post("/create")
@login_required
def create_resume():
    """
    Creates a new resume with default values for the current user.
    It does not require any data in the request body.
    """
    # Find a default template to assign to the new resume.
    default_template = db.session.execute(select(Template).limit(1)).scalar_one_or_none()
    if not default_template:
        return jsonify({"error": "No templates found in the system. Cannot create a resume."}), 500

    # Generate a unique default name for the resume (e.g., "Untitled Resume (2)").
    base_name = "Untitled Resume"
    existing_names_stmt = select(Resume.name).where(
        Resume.user_id == current_user.id,
        Resume.name.like(f"{base_name}%")
    )
    existing_names = db.session.execute(existing_names_stmt).scalars().all()
    
    new_name = base_name
    counter = 1
    while new_name in existing_names:
        counter += 1
        new_name = f"{base_name} ({counter})"

    # Create the new resume object with the default values.
    res = Resume()
    res.user_id = current_user.id
    res.name = new_name
    
    res.resume_name = "Untitled Resume"
    res.template_id = default_template.id
    # Other fields (phone, email, etc.) will be null by default, though we could
    # also default the resume's 'email' field to current_user.email here.
    res.email = current_user.email
    
    res.save_to_db()
    db.session.flush() # Ensure the new ID is available for get_full_resume

    # Fetch the full resume object to return to the frontend.
    new_resume = get_full_resume(res.id, current_user.id, db.session)

    # Return the new resume object with a 201 Created status code.
    if new_resume:
        return jsonify(new_resume.json()), 201
    else:
        # This case should ideally not be reached if creation was successful.
        return jsonify({"error": "Failed to retrieve the created resume."}), 500

@resume_views.put("/update/<int:id>")
@login_required
def update_resume(id: int):
    data = request.get_json()
    if not data or type(data) != dict:
        return jsonify({"error": "Missing required data"}), 400

    resume_to_update = get_full_resume(id, current_user.id, db.session)

    if not resume_to_update:
        return jsonify({"error": "Resume not found or access denied"}), 404

    try:
        updated_resume = process_resume_update(resume_to_update, data, current_user.id, db.session)
        
        db.session.commit()
        
        return jsonify({"message": "Resume updated successfully", "resume": updated_resume.json()})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error during resume update: {e}")
        return jsonify({"error": "An unexpected error occurred while updating the resume."}), 500


@resume_views.delete("/delete/<int:id>")
@login_required
def delete_resume(id: int):
    stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == id))
    result = db.session.execute(stmt).scalar()

    if not result:
        return {"error": "Resume not found"}, 404

    result.delete_from_db()

    return jsonify({"message": "Deleted resume"})


# ==================== Resume Section Routes ====================


@resume_views.get("/section/<int:resume_id>/<int:id>")
@login_required
def get_resume_section(resume_id: int, id: int):
    """
    Get a resume section.
    """
    resume_stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == resume_id))
    resume = db.session.execute(resume_stmt).scalar()
    if not resume:
        return {"error": "Resume not found or access denied"}, 404

    stmt = select(ResumeSection).where(
        and_(
            ResumeSection.user_id == current_user.id,
            ResumeSection.resume_id == resume.id,
            ResumeSection.id == id
        )
    )
    result = db.session.execute(stmt).scalar()
    if result:
        return result.json()
    return {"error": "Resume section not found."}, 404


@resume_views.post("/section/create/<int:resume_id>")
@login_required
def create_resume_section(resume_id: int):
    """
    Create a resume section.
    """
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Missing name"}), 400
    if not data.get("section_type"): 
        return jsonify({"error": "Missing or incorrect section_type"}), 400

    stmt = select(Resume).where(
        and_(Resume.user_id == current_user.id, Resume.id == resume_id)
    )
    resume = db.session.execute(stmt).scalar()
    if not resume:
        return {"error": "Resume id not found or access denied"}, 404

    new_section = ResumeSection()
    new_section.user_id = current_user.id
    new_section.resume_id = resume.id
    new_section.name = data["name"]
    new_section.section_type = data["section_type"]
    if "display_order" in data:
        new_section.display_order = data["display_order"]

    new_section.save_to_db()
    db.session.flush()

    return jsonify({"message": f"Resume section (id = {new_section.id}) created successfully.", "section": new_section.json()})


@resume_views.put("/section/update/<int:resume_id>/<int:id>")
@login_required
def update_resume_section(resume_id: int, id: int):
    """
    Update metadata information about a resume section.
    """
    data = request.get_json()
    if not data or type(data) != dict:
        return jsonify({"error": "Missing required data"}), 400

    stmt_resume = select(Resume).where(
        and_(Resume.user_id == current_user.id, Resume.id == resume_id)
    )
    resume = db.session.execute(stmt_resume).scalar()
    if not resume:
        return {"error": "Resume id not found or access denied"}, 404

    stmt_section = select(ResumeSection).where(
        and_(ResumeSection.user_id == current_user.id, 
             ResumeSection.id == id,
             ResumeSection.resume_id == resume.id) 
    )
    section_to_update = db.session.execute(stmt_section).scalar()
    if not section_to_update:
        return {"error": "Resume section id not found or not associated with this resume"}, 404

    if "name" in data:
        section_to_update.name = data["name"]
    if "section_type" in data:
        section_to_update.section_type = data["section_type"]
    if "display_order" in data:
        section_to_update.display_order = data["display_order"]
    
    section_to_update.save_to_db()
    return jsonify({"message": "Updated resume section", "section": section_to_update.json()})


@resume_views.delete("/section/delete/<int:resume_id>/<int:id>")
@login_required
def delete_resume_section(resume_id: int, id: int):
    """
    Delete a resume section.
    """
    resume_stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == resume_id))
    resume = db.session.execute(resume_stmt).scalar()
    if not resume:
        return {"error": "Resume not found or access denied"}, 404

    stmt = select(ResumeSection).where(
        and_(ResumeSection.user_id == current_user.id,
             ResumeSection.resume_id == resume.id,
             ResumeSection.id == id)
    )
    section_to_delete = db.session.execute(stmt).scalar()

    if not section_to_delete:
        return {"error": "Resume section not found"}, 404

    section_to_delete.delete_from_db()
    return jsonify({"message": "Deleted resume section"})


# ==================== Resume Items Routes ====================


@resume_views.get("/item/<int:id>")
@login_required
def get_resume_item(id: int):
    """
    Get a resume item.
    """
    stmt = select(ResumeItem).where(
        and_(ResumeItem.user_id == current_user.id, ResumeItem.id == id)
    )
    item = db.session.execute(stmt).scalar()
    if item:
        return item.json()
    return {"error": "Resume item not found."}, 404


@resume_views.post("/item/create")
@login_required
def create_resume_item():
    """
    Create a resume item.
    """
    data = request.get_json()
    if not data: return jsonify({"error": "Missing data"}), 400

    required_fields = ["item_type", "title", "organization", "start_date", "location", "description"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing {field}"}), 400
    
    new_item = ResumeItem()
    new_item.user_id = current_user.id
    new_item.item_type = data["item_type"]
    new_item.title = data["title"]
    new_item.organization = data["organization"]
    new_item.start_date = data["start_date"]
    new_item.end_date = data.get("end_date")
    new_item.location = data["location"]
    new_item.description = data["description"]
    
    new_item.save_to_db()
    db.session.flush()
    return jsonify({"message": f"Item (id = {new_item.id}) created", "item": new_item.json()})


@resume_views.put("/item/update/<int:id>")
@login_required
def update_resume_item(id: int):
    """
    Update a resume item.
    """
    data = request.get_json()
    if not data: return jsonify({"error": "Missing data"}), 400
    
    stmt = select(ResumeItem).where(
        and_(ResumeItem.user_id == current_user.id, ResumeItem.id == id)
    )
    item = db.session.execute(stmt).scalar()
    if not item:
        return {"error": "Resume item not found."}, 404

    if "item_type" in data: item.item_type = data["item_type"]
    if "title" in data: item.title = data["title"]
    if "organization" in data: item.organization = data["organization"]
    if "start_date" in data: item.start_date = data["start_date"]
    if "end_date" in data: item.end_date = data["end_date"]
    if "location" in data: item.location = data["location"]
    if "description" in data: item.description = data["description"]
    
    item.save_to_db()
    return jsonify({"message": f"Updated resume item (id = {item.id})", "item": item.json()})


@resume_views.delete("/item/delete/<int:id>")
@login_required
def delete_resume_item(id: int):
    """
    Delete a resume item.
    """
    stmt = select(ResumeItem).where(
        and_(ResumeItem.user_id == current_user.id, ResumeItem.id == id)
    )
    item = db.session.execute(stmt).scalar()
    if not item:
        return {"error": "Resume item not found."}, 404

    item.delete_from_db()

    return jsonify({"message": "Resume item deleted"})
