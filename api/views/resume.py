from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_

from models.user import User
from models.resume import Resume, ResumeSection, ResumeItem
from models.template import Template
from flask_login import login_required, current_user

from db import db
from controllers.resume import process_resume_update, get_full_resume, create_new_resume

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
    assert isinstance(current_user, User)
    resume = get_full_resume(id, current_user, db.session)
    if resume:
        return resume.json()
    return jsonify({"error": "Resume not found"}), 404


@resume_views.post("/create")
@login_required
def create_resume():
    """
    Creates a new resume with default values for the current user using a controller.
    """
    try:
        assert isinstance(current_user, User)
        new_resume = create_new_resume(current_user, db.session)
        db.session.commit()
        # The frontend expects the full resume object directly
        return jsonify(new_resume.json()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error during resume creation: {e}")
        return jsonify({"error": f"An unexpected error occurred. {e}"}), 500


@resume_views.put("/update/<int:id>")
@login_required
def update_resume(id: int):
    data = request.get_json()
    if not data or type(data) is not dict:
        return jsonify({"error": "Missing required data"}), 400

    assert isinstance(current_user, User)
    resume_to_update = get_full_resume(id, current_user, db.session)

    if not resume_to_update:
        return jsonify({"error": "Resume not found or access denied"}), 404

    try:
        process_resume_update(resume_to_update, data, db.session)
        db.session.commit()
        # Re-fetch the entire resume to get the latest state with new IDs
        assert isinstance(current_user, User)
        updated_resume = get_full_resume(id, current_user, db.session)
        if not updated_resume:
            return jsonify({"error": "Could not retrieve updated resume."}), 404
        # The frontend expects the resume object directly
        return jsonify(updated_resume.json())
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error during resume update: {e}")
        return jsonify(
            {"error": f"An unexpected error occurred while updating the resume. {e}"}
        ), 500


@resume_views.delete("/delete/<int:id>")
@login_required
def delete_resume(id: int):
    stmt = select(Resume).where(
        and_(Resume.user_id == current_user.id, Resume.id == id)
    )
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
    resume_stmt = select(Resume).where(
        and_(Resume.user_id == current_user.id, Resume.id == resume_id)
    )
    resume = db.session.execute(resume_stmt).scalar()
    if not resume:
        return {"error": "Resume not found or access denied"}, 404

    stmt = select(ResumeSection).where(
        and_(
            ResumeSection.user_id == current_user.id,
            ResumeSection.resume_id == resume.id,
            ResumeSection.id == id,
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

    return jsonify(
        {
            "message": f"Resume section (id = {new_section.id}) created successfully.",
            "section": new_section.json(),
        }
    )


@resume_views.put("/section/update/<int:resume_id>/<int:id>")
@login_required
def update_resume_section(resume_id: int, id: int):
    """
    Update metadata information about a resume section.
    """
    data = request.get_json()
    if not data or type(data) is not dict:
        return jsonify({"error": "Missing required data"}), 400

    stmt_resume = select(Resume).where(
        and_(Resume.user_id == current_user.id, Resume.id == resume_id)
    )
    resume = db.session.execute(stmt_resume).scalar()
    if not resume:
        return {"error": "Resume id not found or access denied"}, 404

    stmt_section = select(ResumeSection).where(
        and_(
            ResumeSection.user_id == current_user.id,
            ResumeSection.id == id,
            ResumeSection.resume_id == resume.id,
        )
    )
    section_to_update = db.session.execute(stmt_section).scalar()
    if not section_to_update:
        return {
            "error": "Resume section id not found or not associated with this resume"
        }, 404

    if "name" in data:
        section_to_update.name = data["name"]
    if "section_type" in data:
        section_to_update.section_type = data["section_type"]
    if "display_order" in data:
        section_to_update.display_order = data["display_order"]

    section_to_update.save_to_db()
    return jsonify(
        {"message": "Updated resume section", "section": section_to_update.json()}
    )


@resume_views.delete("/section/delete/<int:resume_id>/<int:id>")
@login_required
def delete_resume_section(resume_id: int, id: int):
    """
    Delete a resume section.
    """
    resume_stmt = select(Resume).where(
        and_(Resume.user_id == current_user.id, Resume.id == resume_id)
    )
    resume = db.session.execute(resume_stmt).scalar()
    if not resume:
        return {"error": "Resume not found or access denied"}, 404

    stmt = select(ResumeSection).where(
        and_(
            ResumeSection.user_id == current_user.id,
            ResumeSection.resume_id == resume.id,
            ResumeSection.id == id,
        )
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
    if not data:
        return jsonify({"error": "Missing data"}), 400

    required_fields = [
        "item_type",
        "title",
        "organization",
        "start_date",
        "location",
        "description",
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing {field}"}), 400

    new_item = ResumeItem()
    new_item.user_id = current_user.id
    new_item.title = data["title"]
    new_item.organization = data["organization"]
    new_item.start_date = data["start_date"]
    new_item.end_date = data.get("end_date")
    new_item.location = data["location"]
    new_item.description = data["description"]

    new_item.save_to_db()
    db.session.flush()
    return jsonify(
        {"message": f"Item (id = {new_item.id}) created", "item": new_item.json()}
    )


@resume_views.put("/item/update/<int:id>")
@login_required
def update_resume_item(id: int):
    """
    Update a resume item.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    stmt = select(ResumeItem).where(
        and_(ResumeItem.user_id == current_user.id, ResumeItem.id == id)
    )
    item = db.session.execute(stmt).scalar()
    if not item:
        return {"error": "Resume item not found."}, 404

    if "title" in data:
        item.title = data["title"]
    if "organization" in data:
        item.organization = data["organization"]
    if "start_date" in data:
        item.start_date = data["start_date"]
    if "end_date" in data:
        item.end_date = data["end_date"]
    if "location" in data:
        item.location = data["location"]
    if "description" in data:
        item.description = data["description"]

    item.save_to_db()
    return jsonify(
        {"message": f"Updated resume item (id = {item.id})", "item": item.json()}
    )


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
