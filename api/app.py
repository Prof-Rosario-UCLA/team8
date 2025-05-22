from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

from flask_login import LoginManager

# Load environment variables from .env file if it exists in the 'api' directory
load_dotenv(".flaskenv")

app = Flask(__name__)

# --- CORS Configuration ---
# Allow requests from your Next.js development server (default port 3000)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# Database Configuration
# Using PostgreSQL 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, user_id)

# API Routes
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(message="Pong!")

from routes.auth_routes import auth_routes
app.register_blueprint(auth_routes)

# Main execution
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 