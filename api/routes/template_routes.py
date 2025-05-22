from flask import Blueprint, request, jsonify
from api.controllers import template_controller as ctrl
from uuid import UUID

template_routes = Blueprint("template_routes", __name__, url_prefix="/templates")


@template_routes.route("/", methods=["POST"])
def create_template():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        template = ctrl.create_template(data)
        return jsonify(template), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@template_routes.route("/<uuid:template_id>", methods=["GET"])
def get_template(template_id: UUID):
    try:
        template = ctrl.get_template(template_id)
        return jsonify(template), 200
    except ValueError as e:  # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@template_routes.route("/", methods=["GET"])
def get_all_templates():
    try:
        templates = ctrl.get_all_templates()
        return jsonify(templates), 200
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@template_routes.route("/<uuid:template_id>", methods=["PUT"])
def update_template(template_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        template = ctrl.update_template(template_id, data)
        return jsonify(template), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Or 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500


@template_routes.route("/<uuid:template_id>", methods=["DELETE"])
def delete_template(template_id: UUID):
    try:
        result = ctrl.delete_template(template_id)
        # Controller returns a message which might indicate non-deletion due to usage
        if "cannot be deleted" in result.get("message", "").lower():
            return jsonify(result), 409  # Conflict
        return jsonify(result), 200  # Or 204 if just a success message
    except ValueError as e:  # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify(
            {"error": "An unexpected error occurred", "details": str(e)}
        ), 500
