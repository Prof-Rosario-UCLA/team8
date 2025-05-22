from ..models import db, User, Website, Education, Experience, Project, Resume
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload  # For eager loading related objects
from .website_controller import (
    serialize_website,
    create_website as wc_create,
    update_website as wc_update,
    delete_website as wc_delete,
    get_websites_for_user as wc_get_for_user,
)
from .utils import get_or_404


def serialize_user(user: User, include_details=False):
    """Converts a User object to a dictionary."""
    data = {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat()
        if user.created_at is not None
        else None,
    }
    if include_details:
        data["websites"] = [serialize_website(w) for w in user.websites]

        data["educations_count"] = len(user.educations)
        data["experiences_count"] = len(user.experiences)
        data["projects_count"] = len(user.projects)
        data["resumes_count"] = len(user.resumes)
    return data


def create_user(data):
    """Creates a new user."""
    try:
        user = User(name=data["name"], email=data["email"])
        # TODO: We'll handle auth with OAuth2.0, so no need to hash password here, however we'll need to store the OAuth provider user id
        # Email likely comes from OAuth provider, so no need to validate it here
        db.session.add(user)
        db.session.commit()
        return serialize_user(user)
    except SQLAlchemyError as e:
        db.session.rollback()
        # Log error e
        raise ValueError(f"Error creating user: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for user creation: {str(e)}")


def get_user(user_id, include_details=False):
    """Gets a specific user by ID."""
    query = User.query
    if include_details:
        # Eager load related entities if details are requested
        query = query.options(
            joinedload(User.websites),
            # joinedload(User.educations),
            # joinedload(User.experiences),
            # joinedload(User.projects),
            # joinedload(User.resumes)
        )
    user = query.get_or_404(user_id)
    return serialize_user(user, include_details=include_details)


def get_all_users():
    """Gets all users."""
    users = User.query.all()
    return [serialize_user(user) for user in users]


def update_user(user_id, data):
    """Updates an existing user."""
    try:
        user = get_or_404(User, user_id, "User")

        # Update standard user fields
        if "name" in data:
            user.name = data["name"]
        # Email updates should be handled carefully, possibly requiring verification
        # For now, let's assume it can be updated if provided.
        if "email" in data and data["email"] != user.email:
            # Add validation for email format if not handled by OAuth
            user.email = data["email"]
        if "bio" in data:
            user.bio = data["bio"]
        # ... other user fields ...

        # Handle website updates
        if "websites" in data:
            incoming_websites_data = data["websites"]
            existing_websites = {str(w.id): w for w in user.websites}
            processed_website_ids = set()

            for site_data in incoming_websites_data:
                site_id = site_data.get("id")
                if site_id and str(site_id) in existing_websites:
                    # Update existing website
                    wc_update(site_id, site_data)  # website_controller.update_website
                    processed_website_ids.add(str(site_id))
                elif not site_id:
                    # Create new website
                    # Ensure wc_create associates with this user_id
                    new_site_data = site_data.copy()
                    # wc_create might need user_id explicitly if not inferred
                    wc_create(
                        user_id, new_site_data
                    )  # website_controller.create_website
                # else: site_id provided but not found - could be an error or ignore

            # Delete websites not present in the incoming list
            for site_id_str, site_obj in existing_websites.items():
                if site_id_str not in processed_website_ids:
                    wc_delete(site_obj.id)  # website_controller.delete_website

        db.session.commit()
        # Reload user to get updated websites if necessary for serialization
        db.session.refresh(user)
        # Ensure your serialize_user function handles websites correctly
        return serialize_user(
            user, include_details=True
        )  # Assuming include_details fetches websites
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating user: {str(e)}")


def delete_user(user_id):
    """Deletes a user."""
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting user: {str(e)}")
