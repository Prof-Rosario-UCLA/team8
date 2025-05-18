from flask import Blueprint, request, jsonify
from api.controllers import skill_controller as ctrl
from uuid import UUID

skill_routes = Blueprint('skill_routes', __name__, url_prefix='/skills')

@skill_routes.route('/', methods=['POST'])
def create_skill():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        skill = ctrl.create_skill(data)
        return jsonify(skill), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@skill_routes.route('/<uuid:skill_id>', methods=['GET'])
def get_skill(skill_id: UUID):
    try:
        skill = ctrl.get_skill(skill_id)
        return jsonify(skill), 200
    except ValueError as e: # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@skill_routes.route('/', methods=['GET'])
def get_all_skills():
    try:
        category_filter = request.args.get('category')
        skills = ctrl.get_all_skills(category_filter=category_filter)
        return jsonify(skills), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@skill_routes.route('/<uuid:skill_id>', methods=['PUT'])
def update_skill(skill_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        skill = ctrl.update_skill(skill_id, data)
        return jsonify(skill), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Or 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@skill_routes.route('/<uuid:skill_id>', methods=['DELETE'])
def delete_skill(skill_id: UUID):
    try:
        result = ctrl.delete_skill(skill_id)
        return jsonify(result), 200 # Or 204
    except ValueError as e: # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500 