from flask import Blueprint, request, jsonify
from api.controllers import user_controller as ctrl
from uuid import UUID
from api.controllers import website_controller as website_ctrl

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        user = ctrl.create_user(data)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@user_bp.route('/<uuid:user_id>', methods=['GET'])
def get_user(user_id: UUID):
    try:
        include_details = request.args.get('include_details', 'false').lower() == 'true'
        user = ctrl.get_user(user_id, include_details=include_details)
        return jsonify(user), 200
    except ValueError as e: # Should be caught by get_or_404 in controller if not found
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@user_bp.route('/', methods=['GET'])
def get_all_users():
    try:
        users = ctrl.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@user_bp.route('/<uuid:user_id>', methods=['PUT'])
def update_user(user_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        user = ctrl.update_user(user_id, data)
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Or 404 if user not found
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@user_bp.route('/<uuid:user_id>', methods=['DELETE'])
def delete_user(user_id: UUID):
    try:
        result = ctrl.delete_user(user_id)
        return jsonify(result), 200 # Or 204 if no content
    except ValueError as e: # Should be caught by get_or_404 in controller if not found
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@user_bp.route('/<uuid:user_id>/websites', methods=['POST'])
def create_website_for_user(user_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        website = website_ctrl.create_website(user_id, data)
        return jsonify(website), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@user_bp.route('/<uuid:user_id>/websites', methods=['GET'])
def get_websites_for_user(user_id: UUID):
    try:
        websites = website_ctrl.get_websites_for_user(user_id)
        return jsonify(websites), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
