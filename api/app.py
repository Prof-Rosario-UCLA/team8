from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from flask_migrate import Migrate
from db import db, init_db

from flask_login import LoginManager

import logging

from views.auth import auth_view
from views.resume import resume_views
from views.template import template_views
from views.user import user_views

# Load environment variables from .env file if it exists in the 'api' directory
load_dotenv(".flaskenv")

app = Flask(__name__)
# https://stackoverflow.com/questions/26578733/why-is-flask-application-not-creating-any-logs-when-hosted-by-gunicorn
gunicorn_error_logger = logging.getLogger("gunicorn.error")
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

# --- CORS Configuration ---
CLIENT_ORIGIN = os.environ.get("CLIENT_ORIGIN") or "http://localhost:3000"
# Allow requests from your Next.js development server (default port 3000)
CORS(app, resources={r"/api/*": {"origins": CLIENT_ORIGIN}})


# Database Configuration
# Using PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("DATABASE_URL") or "sqlite:///:memory:"
)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: int):
    from models.user import User

    stmt = db.select(User).filter_by(id=user_id)
    return db.session.execute(stmt).scalar()


# API Routes
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify(message="Pong!")


main_view = Blueprint("main_view", __name__, url_prefix="/api")
main_view.register_blueprint(auth_view)
main_view.register_blueprint(resume_views)
main_view.register_blueprint(template_views)
main_view.register_blueprint(user_views)

app.register_blueprint(main_view)

init_db(app)

# Main execution
if __name__ == "__main__":
    app.run(debug=True, port=5001)
