from flask import Blueprint, request, jsonify
from api.controllers import project_controller as ctrl
from uuid import UUID

project_routes = Blueprint("project_routes", __name__, url_prefix="/projects")

# POST /users/<user_id>/projects
# GET  /users/<user_id>/projects
# GET  /projects/<project_id>
# PUT  /projects/<project_id> (handles bullets and skills)
# DELETE /projects/<project_id>
# POST /projects/<project_id>/skills/<skill_id>
# DELETE /projects/<project_id>/skills/<skill_id>


@project_routes.route("/users/<uuid:user_id>/projects", methods=["POST"])
def create_project_for_user(user_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        project = ctrl.create_project(user_id, data)
        return jsonify(project), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Or 404 if user not found
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@project_routes.route("/users/<uuid:user_id>/projects", methods=["GET"])
def get_all_projects_for_user(user_id: UUID):
    try:
        include_bullets = request.args.get("include_bullets", "false").lower() == "true"
        include_skills = request.args.get("include_skills", "false").lower() == "true"
        projects = ctrl.get_all_projects_for_user(
            user_id, include_bullets=include_bullets, include_skills=include_skills
        )
        return jsonify(projects), 200
    except ValueError as e:  # Controller's get_or_404 for user
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@project_routes.route("/<uuid:project_id>", methods=["GET"])
def get_project(project_id: UUID):
    try:
        include_bullets = request.args.get("include_bullets", "false").lower() == "true"
        include_skills = request.args.get("include_skills", "false").lower() == "true"
        project = ctrl.get_project(
            project_id, include_bullets=include_bullets, include_skills=include_skills
        )
        return jsonify(project), 200
    except ValueError as e:  # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@project_routes.route("/<uuid:project_id>", methods=["PUT"])
def update_project(project_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        project = ctrl.update_project(project_id, data)
        return jsonify(project), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Or 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@project_routes.route("/<uuid:project_id>", methods=["DELETE"])
def delete_project(project_id: UUID):
    try:
        result = ctrl.delete_project(project_id)
        return jsonify(result), 200  # Or 204
    except ValueError as e:  # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@project_routes.route("/<uuid:project_id>/skills/<uuid:skill_id>", methods=["POST"])
def add_skill_to_project(project_id: UUID, skill_id: UUID):
    try:
        project = ctrl.add_skill_to_project(project_id, skill_id)
        return jsonify(project), 200
    except ValueError as e:  # Controller's get_or_404 for project or skill
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@project_routes.route("/<uuid:project_id>/skills/<uuid:skill_id>", methods=["DELETE"])
def remove_skill_from_project(project_id: UUID, skill_id: UUID):
    try:
        project = ctrl.remove_skill_from_project(project_id, skill_id)
        return jsonify(project), 200
    except ValueError as e:  # Controller's get_or_404 for project or skill
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500
