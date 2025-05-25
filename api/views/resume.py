from flask import Blueprint, request, jsonify
from sqlalchemy import select

from models.user import User
from models.resume import Resume, ResumeSection, ResumeItem, ResumeAssociation

from flask_login import login_required, current_user

from db import db

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
    stmt = select(Resume).where(Resume.user_id == current_user.id and Resume.id == id)
    result = db.session.execute(stmt)
    result = result.scalar()
    if result:
        return result.json()
    return {"error": "Resume not found"}, 404


@resume_views.post("/create")
@login_required
def create_resume():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Missing name"}), 400

    res = Resume(user_id=current_user.id, name=data["name"], sections=[])
    res.save_to_db()
    return jsonify({"message": f"Resume (id = {res.id})created successfully"})


@resume_views.put("/update/<int:id>")
@login_required
def update_resume(id: int):
    data = request.get_json()
    if not data or type(data) != dict:
        return jsonify({"error": "Missing required data"})

    stmt = select(Resume).where(Resume.user_id == current_user.id and Resume.id == id)
    result = db.session.execute(stmt)
    result = result.scalar()

    if not result:
        return {"error": "Resume not found"}, 404

    result.name = data.get("name")

    result.save_to_db()

    return jsonify({"message": "Updated resume"})


@resume_views.delete("/delete/<int:id>")
@login_required
def delete_resume(id: int):
    stmt = select(Resume).where(Resume.user_id == current_user.id and Resume.id == id)
    result = db.session.execute(stmt)
    result = result.scalar()

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
    stmt = select(ResumeSection).where(
        ResumeSection.user_id == current_user
        and ResumeSection.resume_id == resume_id
        and ResumeSection.id == id
    )
    result = db.session.execute(stmt)
    result = result.scalar()
    if result:
        return result.json()
    return {"error": "Resume section not found."}, 404


@resume_views.post("/section/create/<int:resume_id>")
@login_required
def create_resume_section(resume_id: int):
    """
    Create a resume section.
    """
    if not resume_id:
        return jsonify({"error": "Missing resume id"}), 400

    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Missing name"}), 400
    # TODO: add validation of section_type
    if not data.get("section_type"):
        return jsonify({"error": "Missing or incorrect section_type"}), 400

    stmt = select(Resume).where(
        Resume.user_id == current_user.id and Resume.id == resume_id
    )
    result = db.session.execute(stmt)
    result = result.scalar()
    if not result:
        return {"error": "Resume id not found"}, 404

    res = ResumeSection(
        user_id=current_user.id,
        resume_id=result.id,
        name=data.get("name"),
        section_type=data.get("section_type"),
        items=[],
    )
    res.save_to_db()

    return {"message": f"Resume section (id = {res.id}) created successfully."}


@resume_views.put("/section/update/<int:resume_id>/<int:id>")
@login_required
def update_resume_section(resume_id: int, id: int):
    """
    Update metadata information about a resume section.
    """
    if not resume_id:
        return jsonify({"error": "Missing resume id"}), 400
    if not id:
        return jsonify({"error": "Missing resume section id"}), 400

    data = request.get_json()
    if not data or type(data) != dict:
        return jsonify({"error": "Missing required data"})

    stmt = select(Resume).where(
        Resume.user_id == current_user.id and Resume.id == resume_id
    )
    result = db.session.execute(stmt)
    result = result.scalar()
    if not result:
        return {"error": "Resume id not found"}, 404

    stmt = select(ResumeSection).where(
        Resume.user_id == current_user.id and ResumeSection.id == id
    )
    section_result = db.session.execute(stmt)
    section_result = section_result.scalar()
    if not section_result:
        return {"error": "Resume section id not found"}, 404

    section_result.resume_id = resume_id
    section_result.name = data.get("name", section_result.name)
    section_result.section_type = data.get("section_type", section_result.section_type)

    section_result.save_to_db()

    return {"message": "Updated resume section"}


@resume_views.delete("/section/delete/<int:resume_id>/<int:id>")
@login_required
def delete_resume_section(resume_id: int, id: int):
    """
    Delete a resume section.
    """
    stmt = select(ResumeSection).where(
        ResumeSection.user_id == current_user.id
        and ResumeSection.resume_id == resume_id
        and ResumeSection.id == id
    )
    result = db.session.execute(stmt)
    result = result.scalar()

    if not result:
        return {"error": "Resume not found"}, 404

    result.delete_from_db()

    return jsonify({"message": "Deleted resume"})


@resume_views.patch("/section/link/<int:resume_id>/<int:id>/<int:item_id>")
@login_required
def link_resume_item_to_section(resume_id: int, id: int, item_id: int):
    if not resume_id:
        return jsonify({"error": "Missing resume id"}), 400

    if not id:
        return jsonify({"error": "Missing resume section id"}), 400

    if not item_id:
        return jsonify({"error": "Missing resume item id"}), 400

    stmt = select(ResumeSection).where(
        ResumeSection.user_id == current_user
        and ResumeSection.resume_id == resume_id
        and ResumeSection.id == id
    )
    section = db.session.execute(stmt)
    section = section.scalar()
    if not section:
        return jsonify({"error": "Resume section not found"}), 404

    stmt = select(ResumeItem).where(
        ResumeItem.user_id == current_user and ResumeItem.id == id
    )
    item = db.session.execute(stmt)
    item = section.scalar()
    if not item:
        return jsonify({"error": "Resume item not found"}), 404

    # Create an association between the section and item
    assoc = ResumeAssociation(user_id=current_user.id, section=section.id, item=item.id)
    assoc.save_to_db()

    return {"message": "Linked resume section to item"}


@resume_views.patch("/section/unlink/<int:resume_id>/<int:id>/<int:item_id>")
@login_required
def unlinklink_resume_item_to_section(resume_id: int, id: int, item_id: int):
    if not resume_id:
        return jsonify({"error": "Missing resume id"}), 400

    if not id:
        return jsonify({"error": "Missing resume section id"}), 400

    if not item_id:
        return jsonify({"error": "Missing resume item id"}), 400

    stmt = select(ResumeSection).where(
        ResumeSection.user_id == current_user
        and ResumeSection.resume_id == resume_id
        and ResumeSection.id == id
    )
    section = db.session.execute(stmt)
    section = section.scalar()
    if not section:
        return jsonify({"error": "Resume section not found"}), 404

    stmt = select(ResumeItem).where(
        ResumeItem.user_id == current_user and ResumeItem.id == id
    )
    item = db.session.execute(stmt)
    item = section.scalar()
    if not item:
        return jsonify({"error": "Resume item not found"}), 404

    # Delete association between the section and item
    stmt = select(ResumeAssociation).where(
        ResumeAssociation.user_id == current_user
        and ResumeAssociation.section == section.id
        and ResumeAssociation.item == item.id
    )
    assoc = db.session.execute(stmt)
    assoc = assoc.scalar()
    if not assoc:
        return {"error": "Link not found"}, 404

    assoc.delete_from_db()

    return {"message": "Unlinked resume section to item"}


# ==================== Resume Items Routes ====================


@resume_views.get("/item/<int:id>")
@login_required
def get_resume_item(id: int):
    """
    Get a resume item.
    """
    stmt = select(ResumeItem).where(
        ResumeItem.user_id == current_user and ResumeItem.id == id
    )
    result = db.session.execute(stmt)
    result = result.scalar()
    if result:
        return result.json()
    return {"error": "Resume item not found."}, 404


@resume_views.post("/item/create")
@login_required
def create_resume_item():
    """
    Create a resume item.
    """
    data = request.get_json()
    if not data.get("item_type"):
        return jsonify({"error": "Missing item_type"}), 400
    if not data.get("title"):
        return jsonify({"error": "Missing title"}), 400
    if not data.get("organization"):
        return jsonify({"error": "Missing organization"}), 400
    if not data.get("start_date"):
        return jsonify({"error": "Missing organization"}), 400
    if not data.get("end_date"):
        return jsonify({"error": "Missing end_date"}), 400
    if not data.get("location"):
        return jsonify({"error": "Missing location"}), 400
    if not data.get("description"):
        return jsonify({"error": "Missing description"}), 400

    item = ResumeItem(
        user_id=current_user.id,
        item_type=data.get("item_type"),
        title=data.get("title"),
        organization=data.get("organization"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        location=data.get("location"),
        description=data.get("description"),
    )
    item.save_to_db()

    return {"message": f"Item (id = {item.id}) created"}


@resume_views.post("/item/update/<int:id>")
@login_required
def update_resume_item(id: int):
    """
    Update a resume item.
    """

    if not id:
        return {"error": "Missing resume item id"}, 400

    data = request.get_json()
    if not data.get("item_type"):
        return jsonify({"error": "Missing item_type"}), 400
    if not data.get("title"):
        return jsonify({"error": "Missing title"}), 400
    if not data.get("organization"):
        return jsonify({"error": "Missing organization"}), 400
    if not data.get("start_date"):
        return jsonify({"error": "Missing organization"}), 400
    if not data.get("end_date"):
        return jsonify({"error": "Missing end_date"}), 400
    if not data.get("location"):
        return jsonify({"error": "Missing location"}), 400
    if not data.get("description"):
        return jsonify({"error": "Missing description"}), 400

    stmt = select(ResumeItem).where(
        ResumeItem.user_id == current_user.id and ResumeItem.id == id
    )
    query = db.session.execute(stmt)
    item = query.scalar()
    if not item:
        return {"error": "Resume item not found."}, 404

    item.user_id = (current_user.id,)
    item.item_type = (data.get("item_type", item.item_type),)
    item.title = (data.get("title", item.title),)
    item.organization = (data.get("organization", item.organization),)
    item.start_date = (data.get("start_date", item.start_date),)
    item.end_date = (data.get("end_date", item.end_date),)
    item.location = (data.get("location", item.location),)
    item.description = data.get("description", item.description)

    return {"message": f"Updated resume item (id = {item.id})"}


@resume_views.delete("/item/delete/<int:id>")
@login_required
def delete_resume_item(id: int):
    """
    Delete a resume item.
    """
    if not id:
        return {"error": "Missing resume item id"}, 400

    stmt = select(ResumeItem).where(
        ResumeItem.user_id == current_user.id and ResumeItem.id == id
    )
    query = db.session.execute(stmt)
    item = query.scalar()
    if not item:
        return {"error": "Resume item not found."}, 404

    item.delete_from_db()

    return {"message": "Resume item deleted"}
