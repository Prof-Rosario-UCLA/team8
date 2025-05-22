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
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#     "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
# )
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str):
    from models.user import User

    print(user_id)
    try:
        uid = uuid.UUID(user_id)
    except:
        return None

    return db.session.execute(db.select(User).filter_by(id=uid)).fetchone()[0]


# API Routes
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify(message="Pong!")


from routes.auth import auth_routes

app.register_blueprint(auth_routes)

# Main execution
if __name__ == "__main__":
    init_db(app)
    app.run(ssl_context="adhoc", debug=True, port=5001)
