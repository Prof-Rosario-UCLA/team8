from flask import Blueprint, request, jsonify
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from models.user import User
from models.resume import Resume, ResumeItem

from flask_login import login_required, current_user

from db import db

resume_routes = Blueprint("resume_routes", __name__, url_prefix="/resumes")

@resume_routes.get("/all")
@login_required
def get_all_resumes():
    """
    Return all resumes belonging to a user.
    """
    stmt = select(Resume).where(Resume.user_id == current_user.id)
    result = db.session.execute(stmt)
    result = result.scalars().all()
    result = [r.json() for r in result]

    return jsonify({
        "resumes": result
    })

@resume_routes.post("/create")
@login_required
def create_resume():
    data = request.get_json()
    if not data.get("title"):
        return jsonify({
            "error": "Missing title"
        }), 400

    res = Resume(
        user_id=current_user.id,
        title=data["title"],
        education=[]
    )
    db.session.add(res)
    db.session.commit()
    return jsonify({
        "message": "Resume created successfully"
    })

# @resume_routes.route("", methods=["POST"])
# def create_resume_route():
#     """Create a new resume."""
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Request body must be JSON"}), 400
#     if "user_id" not in data:  # Basic validation
#         return jsonify({"error": "Missing 'user_id' in request body"}), 400
#     try:
#         resume = resume.create_resume(data)
#         return jsonify(resume), 201
#     except (ValueError, SQLAlchemyError) as e:
#         return jsonify(
#             {"error": str(e)}
#         ), 400  # SQLAlchemyError might be 500 depending on policy
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_routes.route("/<uuid:resume_id>", methods=["GET"])
# def get_resume_route(resume_id: UUID):
#     """Get a specific resume with all its details."""
#     try:
#         resume = resume.get_resume(resume_id)
#         return jsonify(resume), 200
#     except ValueError as e:  # Handles 404 from get_or_404
#         return jsonify({"error": str(e)}), 404
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_routes.route("/<uuid:resume_id>", methods=["PUT"])
# def update_resume_route(resume_id: UUID):
#     """Update resume metadata (e.g., title, template_id)."""
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Request body must be JSON"}), 400
#     try:
#         resume = resume.update_resume(resume_id, data)
#         return jsonify(resume), 200
#     except ValueError as e:  # Handles 404 or validation errors
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_routes.route("/<uuid:resume_id>", methods=["DELETE"])
# def delete_resume_route(resume_id: UUID):
#     """Delete a resume."""
#     try:
#         result = resume.delete_resume(resume_id)
#         return jsonify(result), 200  # Or 204 No Content
#     except ValueError as e:  # Handles 404
#         return jsonify({"error": str(e)}), 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# #  Resume Section CRUD & Ordering


# @resume_routes.route("/<uuid:resume_id>/sections", methods=["POST"])
# def add_section_to_resume_route(resume_id: UUID):
#     """Add a new section to a resume."""
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Request body must be JSON"}), 400
#     try:
#         section = resume.create_resume_section(resume_id, data)
#         return jsonify(section), 201
#     except ValueError as e:
#         return jsonify({"error": str(e)}), 400
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_routes.route(
#     "/<uuid:resume_id>/sections/<string:section_type_str>", methods=["DELETE"]
# )
# def remove_section_from_resume_route(resume_id: UUID, section_type_str: str):
#     """Remove a section from a resume by its type string."""
#     try:
#         result = resume.delete_resume_section(resume_id, section_type_str)
#         return jsonify(result), 200
#     except ValueError as e:  # Handles 404 or invalid type
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# @resume_routes.route("/<uuid:resume_id>/sections/order", methods=["PUT"])
# def update_resume_sections_order_route(resume_id: UUID):
#     """Update the order of sections within a resume."""
#     data = request.get_json()
#     if not isinstance(data, list):
#         return jsonify(
#             {"error": "Request body must be a list of section order data"}
#         ), 400
#     try:
#         updated_resume = resume.update_resume_sections_order(resume_id, data)
#         return jsonify(updated_resume), 200
#     except ValueError as e:  # Handles 404 or validation errors
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500


# #  Resume Item Operations


# @resume_routes.route("/<uuid:resume_id>/items", methods=["POST"])
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


# @resume_routes.route(
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


# @resume_routes.route(
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


# @resume_routes.route("/<uuid:resume_id>/items/order", methods=["PUT"])
# def reorder_resume_items_route(resume_id: UUID):
#     """Reorder items within a resume."""
#     data = request.get_json()
#     if not data or "items" not in data or not isinstance(data["items"], list):
#         return jsonify({"error": "Request body must be JSON with an 'items' list"}), 400
#     if "items_type" not in data or not isinstance(data["items_type"], str):
#         return jsonify(
#             {"error": "Request body must contain 'items_type' with a string value."}
#         ), 400
#     try:
#         updated_resume = resume.reorder_resume_items(resume_id, data)
#         return jsonify(updated_resume), 200
#     except ValueError as e:  # Handles 404 or validation errors
#         return jsonify({"error": str(e)}), 400 if "not found" not in str(
#             e
#         ).lower() else 404
#     except SQLAlchemyError as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500
#     except Exception as e:
#         return jsonify({"error": "An unexpected error occurred"}), 500
