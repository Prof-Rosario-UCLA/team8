from flask import Blueprint, request, jsonify
from api.controllers import education_controller as ctrl
from uuid import UUID

education_routes = Blueprint("education_routes", __name__, url_prefix="/educations")

# POST /users/<user_id>/educations
# GET  /users/<user_id>/educations
# GET  /educations/<education_id>
# PUT  /educations/<education_id> (handles bullet updates too)
# DELETE /educations/<education_id>


@education_routes.route("/users/<uuid:user_id>/educations", methods=["POST"])
def create_education_for_user(user_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        education = ctrl.create_education(user_id, data)
        return jsonify(education), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Or 404 if user not found
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@education_routes.route("/users/<uuid:user_id>/educations", methods=["GET"])
def get_all_educations_for_user(user_id: UUID):
    try:
        include_bullets = request.args.get("include_bullets", "false").lower() == "true"
        educations = ctrl.get_all_educations_for_user(
            user_id, include_bullets=include_bullets
        )
        return jsonify(educations), 200
    except ValueError as e:  # Controller's get_or_404 for user
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@education_routes.route("/<uuid:education_id>", methods=["GET"])
def get_education(education_id: UUID):
    try:
        include_bullets = request.args.get("include_bullets", "false").lower() == "true"
        education = ctrl.get_education(education_id, include_bullets=include_bullets)
        return jsonify(education), 200
    except ValueError as e:  # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@education_routes.route("/<uuid:education_id>", methods=["PUT"])
def update_education(education_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        education = ctrl.update_education(education_id, data)
        return jsonify(education), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Or 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@education_routes.route("/<uuid:education_id>", methods=["DELETE"])
def delete_education(education_id: UUID):
    try:
        result = ctrl.delete_education(education_id)
        return jsonify(result), 200  # Or 204
    except ValueError as e:  # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500
