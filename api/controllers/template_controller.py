from ..models import db, Template, Resume
from sqlalchemy.exc import SQLAlchemyError

def serialize_template(template: Template):
    """Converts a Template object to a dictionary."""
    return {
        'id': str(template.id),
        'name': template.name,
        'uri': template.uri
    }

def create_template(data):
    """Creates a new template."""
    try:
        template = Template(
            name=data.get('name'),
            uri=data['uri']
        )
        db.session.add(template)
        db.session.commit()
        return serialize_template(template)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating template: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for template creation: {str(e)}")


def get_template(template_id):
    """Gets a specific template by ID."""
    template = Template.query.get_or_404(template_id)
    return serialize_template(template)


def get_all_templates():
    """Gets all templates."""
    templates = Template.query.order_by(Template.name).all()
    return [serialize_template(t) for t in templates]


def update_template(template_id, data):
    """Updates an existing template."""
    template = Template.query.get_or_404(template_id)
    try:
        if 'name' in data:
            template.name = data['name']
        if 'uri' in data:
            template.uri = data['uri']
        
        db.session.commit()
        return serialize_template(template)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating template: {str(e)}")


def delete_template(template_id):
    """Deletes a template."""
    template = Template.query.get_or_404(template_id)
    try:
        # Prevent deletion if in use on a resume
        # find all resumes that use this template
        resumes = Resume.query.filter_by(template_id=template_id).all()
        if resumes:
            return {"message": "Template cannot be deleted because it is in use on a resume"}
        
        # delete the template
        db.session.delete(template)
        db.session.commit()
        return {"message": "Template deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting template: {str(e)}") 