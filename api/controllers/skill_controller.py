from ..models import db, Skill, SkillCategory
from sqlalchemy.exc import SQLAlchemyError


def serialize_skill(skill: Skill):
    """Converts a Skill object to a dictionary."""
    return {
        "id": str(skill.id),
        "name": skill.name,
        "category": skill.category.value if skill.category is not None else None,
    }


def create_skill(data):
    """Creates a new skill."""
    try:
        category_enum = None
        if "category" in data and data["category"]:
            try:
                category_enum = SkillCategory[data["category"]]
            except KeyError:
                raise ValueError(f"Invalid skill category: {data['category']}")

        skill = Skill(name=data["name"], category=category_enum)
        db.session.add(skill)
        db.session.commit()
        return serialize_skill(skill)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating skill: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for skill creation: {str(e)}")


def get_skill(skill_id):
    """Gets a specific skill by ID."""
    skill = Skill.query.get_or_404(skill_id)
    return serialize_skill(skill)


def get_all_skills(category_filter=None):
    """Gets all skills, optionally filtered by category."""
    query = Skill.query
    if category_filter:
        try:
            category_enum = SkillCategory[category_filter]
            query = query.filter_by(category=category_enum)
        except KeyError:
            # Optionally, handle invalid category filter (e.g., return empty list or error)
            pass
    skills = query.order_by(Skill.name).all()
    return [serialize_skill(s) for s in skills]


def update_skill(skill_id, data):
    """Updates an existing skill."""
    skill = Skill.query.get_or_404(skill_id)
    try:
        if "name" in data:
            skill.name = data["name"]
        if "category" in data:
            if data["category"]:
                try:
                    skill.category = SkillCategory[data["category"]]
                except KeyError:
                    raise ValueError(f"Invalid skill category: {data['category']}")
            else:
                skill.category = None  # Allow unsetting category

        db.session.commit()
        return serialize_skill(skill)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating skill: {str(e)}")


def delete_skill(skill_id):
    """Deletes a skill."""
    skill = Skill.query.get_or_404(skill_id)
    try:
        # Note: Deleting a skill will also remove it from experience_skills and project_skills
        # due to ondelete="CASCADE" in the ForeignKey definitions of those tables.
        db.session.delete(skill)
        db.session.commit()
        return {"message": "Skill deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting skill: {str(e)}")
