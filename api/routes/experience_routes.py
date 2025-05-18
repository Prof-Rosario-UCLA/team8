from flask import Blueprint, request, jsonify
from api.controllers import experience_controller as ctrl
from uuid import UUID

experience_bp = Blueprint('experience_bp', __name__, url_prefix='/experiences')

# POST /users/<user_id>/experiences
# GET  /users/<user_id>/experiences
# GET  /experiences/<experience_id>
# PUT  /experiences/<experience_id> (handles bullets and skills)
# DELETE /experiences/<experience_id>
# POST /experiences/<experience_id>/skills/<skill_id>
# DELETE /experiences/<experience_id>/skills/<skill_id>

@experience_bp.route('/users/<uuid:user_id>/experiences', methods=['POST'])
def create_experience_for_user(user_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        experience = ctrl.create_experience(user_id, data)
        return jsonify(experience), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Or 404 if user not found
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@experience_bp.route('/users/<uuid:user_id>/experiences', methods=['GET'])
def get_all_experiences_for_user(user_id: UUID):
    try:
        include_bullets = request.args.get('include_bullets', 'false').lower() == 'true'
        include_skills = request.args.get('include_skills', 'false').lower() == 'true'
        experiences = ctrl.get_all_experiences_for_user(user_id, include_bullets=include_bullets, include_skills=include_skills)
        return jsonify(experiences), 200
    except ValueError as e: # Controller's get_or_404 for user
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@experience_bp.route('/<uuid:experience_id>', methods=['GET'])
def get_experience(experience_id: UUID):
    try:
        include_bullets = request.args.get('include_bullets', 'false').lower() == 'true'
        include_skills = request.args.get('include_skills', 'false').lower() == 'true'
        experience = ctrl.get_experience(experience_id, include_bullets=include_bullets, include_skills=include_skills)
        return jsonify(experience), 200
    except ValueError as e: # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@experience_bp.route('/<uuid:experience_id>', methods=['PUT'])
def update_experience(experience_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        experience = ctrl.update_experience(experience_id, data)
        return jsonify(experience), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Or 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@experience_bp.route('/<uuid:experience_id>', methods=['DELETE'])
def delete_experience(experience_id: UUID):
    try:
        result = ctrl.delete_experience(experience_id)
        return jsonify(result), 200 # Or 204
    except ValueError as e: # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@experience_bp.route('/<uuid:experience_id>/skills/<uuid:skill_id>', methods=['POST'])
def add_skill_to_experience(experience_id: UUID, skill_id: UUID):
    try:
        experience = ctrl.add_skill_to_experience(experience_id, skill_id)
        return jsonify(experience), 200
    except ValueError as e: # Controller's get_or_404 for experience or skill
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@experience_bp.route('/<uuid:experience_id>/skills/<uuid:skill_id>', methods=['DELETE'])
def remove_skill_from_experience(experience_id: UUID, skill_id: UUID):
    try:
        experience = ctrl.remove_skill_from_experience(experience_id, skill_id)
        return jsonify(experience), 200
    except ValueError as e: # Controller's get_or_404 for experience or skill
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
