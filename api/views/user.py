from flask import Blueprint

from sqlalchemy import select

from models.user import User

from flask_login import login_required, current_user

from cache import cache_response

from db import db

user_views = Blueprint("user_views", __name__, url_prefix="/user")


@user_views.get("/me")
@login_required
@cache_response
def get_myself():
    """
    Retrieve information about the current user.
    """
    stmt = select(User).where(User.id == current_user.id)
    result = db.session.execute(stmt)
    result = result.scalar()
    assert result is not None  # If the user is logged in, there should always be a user
    return result.json()
