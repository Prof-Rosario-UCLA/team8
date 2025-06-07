from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_, func, delete

from models.user import User
from models.resume import Resume, ResumeSection, ResumeItem, ResumeAssociation

from flask_login import login_required, current_user

from db import db
from controllers.resume import process_resume_update

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
    with a given resume id.
    """
    stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == id))
    result = db.session.execute(stmt)
    result = result.scalar()
    if result:
        return result.json()
    return {"error": "Resume not found"}, 404


@resume_views.post("/create")
@login_required
def create_resume():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Missing name"}), 400
    if not data.get("resume_name"):
        return jsonify({"error": "Missing resume_name"}), 400
    if not data.get("template_id"):
        return jsonify({"error": "Missing template_id"}), 400

    res = Resume()
    res.user_id = current_user.id
    res.name = data["name"]
    res.resume_name = data["resume_name"]
    res.template_id = data["template_id"]
    if "phone" in data:
        res.phone = data["phone"]
    if "email" in data:
        res.email = data["email"]
    if "linkedin" in data:
        res.linkedin = data["linkedin"]
    if "github" in data:
        res.github = data["github"]
    if "website" in data:
        res.website = data["website"]
        
    res.save_to_db()
    return jsonify({"message": f"Resume (id = {res.id})created successfully"})


@resume_views.put("/update/<int:id>")
@login_required
def update_resume(id: int):
    data = request.get_json()
    if not data or type(data) != dict:
        return jsonify({"error": "Missing required data"}), 400

    stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == id))
    resume_to_update = db.session.execute(stmt).scalar_one_or_none()

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


@resume_views.patch("/section/link/<int:resume_id>/<int:section_id>/<int:item_id>")
@login_required
def link_resume_item_to_section(resume_id: int, section_id: int, item_id: int):
    data = request.get_json()

    resume_check_stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == resume_id))
    if not db.session.execute(resume_check_stmt).scalar():
        return jsonify({"error": "Resume not found or access denied"}), 404

    section_stmt = select(ResumeSection).where(
        and_(ResumeSection.user_id == current_user.id,
             ResumeSection.resume_id == resume_id,
             ResumeSection.id == section_id)
    )
    section = db.session.execute(section_stmt).scalar()
    if not section:
        return jsonify({"error": "Resume section not found or not part of this resume"}), 404

    item_stmt = select(ResumeItem).where(
        and_(ResumeItem.user_id == current_user.id, ResumeItem.id == item_id)
    )
    item = db.session.execute(item_stmt).scalar()
    if not item:
        return jsonify({"error": "Resume item not found or access denied"}), 404

    existing_assoc_stmt = select(ResumeAssociation).where(
        and_(ResumeAssociation.section_id == section.id,
             ResumeAssociation.item_id == item.id,
             ResumeAssociation.user_id == current_user.id) 
    )
    if db.session.execute(existing_assoc_stmt).scalar():
        return jsonify({"error": "Item already linked to this section"}), 400
    
    display_order_val = data.get("display_order") if data else None

    if display_order_val is None: 
        max_order_stmt = select(func.max(ResumeAssociation.display_order)).where(
            and_(ResumeAssociation.user_id == current_user.id,
                 ResumeAssociation.section_id == section.id)
        )
        max_order = db.session.execute(max_order_stmt).scalar()
        display_order_val = (max_order or -1) + 1
    
    assoc = ResumeAssociation()
    assoc.user_id = current_user.id
    assoc.section_id = section.id
    assoc.item_id = item.id
    assoc.display_order = display_order_val
    assoc.save_to_db()
    db.session.flush()

    return jsonify({"message": "Linked resume section to item", "association": assoc.json()})


@resume_views.patch("/section/unlink/<int:resume_id>/<int:section_id>/<int:item_id>")
@login_required
def unlink_resume_item_from_section(resume_id: int, section_id: int, item_id: int):
    resume_check_stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == resume_id))
    if not db.session.execute(resume_check_stmt).scalar():
        return jsonify({"error": "Resume not found or access denied"}), 404
    
    stmt = select(ResumeAssociation).where(
        and_(ResumeAssociation.user_id == current_user.id,
             ResumeAssociation.section_id == section_id,
             ResumeAssociation.item_id == item_id)
    )
    assoc = db.session.execute(stmt).scalar()
    if not assoc:
        return {"error": "Link not found"}, 404

    assoc.delete_from_db()
    return jsonify({"message": "Unlinked resume item from section"})


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

    assoc_stmt = delete(ResumeAssociation).where(
        and_(ResumeAssociation.item_id == item.id, ResumeAssociation.user_id == current_user.id)
    )
    db.session.execute(assoc_stmt)
    
    item.delete_from_db()

    return jsonify({"message": "Resume item deleted"})
