from flask import Flask, jsonify
from flask_cors import CORS
import os, uuid
from dotenv import load_dotenv

from db import db, init_db

from flask_login import LoginManager

# Load environment variables from .env file if it exists in the 'api' directory
load_dotenv(".flaskenv")

app = Flask(__name__)

# --- CORS Configuration ---
# Allow requests from your Next.js development server (default port 3000)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# Database Configuration
# Using PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_routes.index"


@login_manager.user_loader
def load_user(user_id: int):
    from models.user import User
    stmt = db.select(User).filter_by(id=user_id)
    return db.session.execute(stmt).scalar()


# API Routes
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify(message="Pong!")


from views.auth import auth_routes
from views.resume import resume_routes

app.register_blueprint(auth_routes)
app.register_blueprint(resume_routes)

# Main execution
if __name__ == "__main__":
    init_db(app)
    app.run(ssl_context="adhoc", debug=True, port=5001)
