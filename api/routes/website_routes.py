from flask import Blueprint, request, jsonify
from api.controllers import website_controller as ctrl
from uuid import UUID

website_routes = Blueprint('website_routes', __name__, url_prefix='/websites')

# Note: Websites are often tied to a user.
# POST /users/<user_id>/websites
# GET  /users/<user_id>/websites
# GET  /websites/<website_id> (if global access needed, or for simplicity)
# PUT  /websites/<website_id>
# DELETE /websites/<website_id>

@website_routes.route('/users/<uuid:user_id>/websites', methods=['POST'])
def create_website_for_user(user_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        website = ctrl.create_website(user_id, data)
        return jsonify(website), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Could be 404 if user not found
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@website_routes.route('/users/<uuid:user_id>/websites', methods=['GET'])
def get_websites_for_user(user_id: UUID):
    try:
        websites = ctrl.get_websites_for_user(user_id)
        return jsonify(websites), 200
    except ValueError as e: # Controller's get_or_404 for user
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@website_routes.route('/<uuid:website_id>', methods=['GET'])
def get_website(website_id: UUID):
    try:
        website = ctrl.get_website(website_id)
        return jsonify(website), 200
    except ValueError as e: # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@website_routes.route('/<uuid:website_id>', methods=['PUT'])
def update_website(website_id: UUID):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        website = ctrl.update_website(website_id, data)
        return jsonify(website), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Or 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@website_routes.route('/<uuid:website_id>', methods=['DELETE'])
def delete_website(website_id: UUID):
    try:
        result = ctrl.delete_website(website_id)
        return jsonify(result), 200 # Or 204
    except ValueError as e: # Controller's get_or_404
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500 