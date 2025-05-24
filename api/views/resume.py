from flask import Blueprint, request, jsonify
from sqlalchemy import select

from models.user import User
from models.resume import Resume, ResumeItem

from flask_login import login_required, current_user

from db import db

resume_views = Blueprint("resume_views", __name__, url_prefix="/resumes")


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
    return jsonify({"message": "Resume created successfully"})


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


# #  Resume Item Operations


# @resume_views.route("/<uuid:resume_id>/items", methods=["POST"])
# def add_item_to_resume_route(resume_id: UUID):
#     """Add a global item (Education, Experience, Project) to a resume."""
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Request body must be JSON"}), 400
#     # Basic validation for required fields
#     required_fields = ["item_type", "item_id", "section_id"]
#     if not all(field in data for field in required_fields):
#         return jsonify(
#             {
#                 "error": f"Missing one or more required fields: {', '.join(required_fields)}"
#             }
#         ), 400
#     try:
#         resume_item_detail = resume.add_item_to_resume(resume_id, data)
#         return jsonify(resume_item_detail), 201
#     except ValueError as e:  # Handles 404 or validation errors
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_views.route(
#     "/<uuid:resume_id>/items/<item_type_str>/<uuid:item_id>", methods=["PUT"]
# )
# def update_resume_item_route(resume_id: UUID, item_type_str: str, item_id: UUID):
#     """
#     Update a specific item within a resume.
#     The backend will diff the provided data against the global item.
#     """
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Request body must be JSON"}), 400
#     if "content" not in data or "data" not in data["content"]:
#         return jsonify(
#             {"error": "Request body must contain 'content' with a 'data' object."}
#         ), 400

#     try:
#         updated_item_detail = resume.update_resume_item(
#             resume_id, item_type_str, item_id, data
#         )
#         return jsonify(updated_item_detail), 200
#     except ValueError as e:  # Handles 404 or validation errors
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_views.route(
#     "/<uuid:resume_id>/items/<item_type_str>/<uuid:item_id>", methods=["DELETE"]
# )
# def remove_item_from_resume_route(resume_id: UUID, item_type_str: str, item_id: UUID):
#     """Remove an item from a resume."""
#     try:
#         result = resume.remove_item_from_resume(resume_id, item_type_str, item_id)
#         return jsonify(result), 200
#     except ValueError as e:  # Handles 404 or validation errors
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500
