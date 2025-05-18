from ..models import db, User, Website
from sqlalchemy.exc import SQLAlchemyError

def serialize_website(website: Website):
    """Converts a Website object to a dictionary."""
    return {
        'id': str(website.id),
        'user_id': str(website.user_id),
        'alt': website.alt,
        'url': website.url
    }

def create_website(user_id, data):
    """Creates a new website for a user."""
    user = User.query.get_or_404(user_id) # Ensure user exists
    try:
        website = Website(
            user_id=user.id,
            alt=data.get('alt'),
            url=data['url']
        )
        db.session.add(website)
        db.session.commit()
        return serialize_website(website)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating website: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for website creation: {str(e)}")


def get_website(website_id):
    """Gets a specific website by ID."""
    website = Website.query.get_or_404(website_id)
    return serialize_website(website)


def get_websites_for_user(user_id):
    """Gets all websites for a specific user."""
    user = User.query.get_or_404(user_id)
    websites = Website.query.filter_by(user_id=user.id).all()
    return [serialize_website(w) for w in websites]


def update_website(website_id, data):
    """Updates an existing website."""
    website = Website.query.get_or_404(website_id)
    try:
        if 'alt' in data:
            website.alt = data['alt']
        if 'url' in data:
            website.url = data['url']
        
        db.session.commit()
        return serialize_website(website)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating website: {str(e)}")


def delete_website(website_id):
    """Deletes a website."""
    website = Website.query.get_or_404(website_id)
    try:
        db.session.delete(website)
        db.session.commit()
        return {"message": "Website deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting website: {str(e)}") 