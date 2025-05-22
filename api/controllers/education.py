from ..models import db, User, Education, BulletPoint, ParentType
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import Optional, List
from uuid import UUID
from .bullet_point import serialize_bullet_point
from .utils import get_or_404, get_resolved_field
import datetime

# Assuming serialize_bullet might be moved to a shared util or imported from resume_controller for now
# For this example, let's assume it's accessible or we redefine a similar local version if needed.


def serialize_education(
    education_instance: Education,
    field_overrides_dict: Optional[dict] = None,
    include_bullets_if_no_override: bool = False,
):
    """
    Serializes an Education instance.
    If field_overrides_dict is provided, applies overrides and returns only resolved data fields.
    Otherwise, serializes global data and can include bullets based on include_bullets_if_no_override.
    """
    if not education_instance:
        return None

    overrides = field_overrides_dict or {}
    is_resume_context = bool(field_overrides_dict)

    data = {
        "id": str(education_instance.id),
        "user_id": str(education_instance.user_id),
        "school": get_resolved_field(
            education_instance, overrides, "school", education_instance.school
        ),
        "degree": get_resolved_field(
            education_instance, overrides, "degree", education_instance.degree
        ),
        "major": get_resolved_field(
            education_instance, overrides, "major", education_instance.major
        ),
        "desc_long": get_resolved_field(
            education_instance,
            overrides,
            "desc_long",
            getattr(education_instance, "desc_long", None),
        ),
    }

    raw_start_date = get_resolved_field(
        education_instance, overrides, "start", education_instance.start
    )
    if isinstance(raw_start_date, (datetime.date, datetime.datetime)):
        data["start"] = raw_start_date.isoformat()
    else:
        data["start"] = raw_start_date

    raw_end_date = get_resolved_field(
        education_instance, overrides, "end", education_instance.end
    )
    if isinstance(raw_end_date, (datetime.date, datetime.datetime)):
        data["end"] = raw_end_date.isoformat()
    else:
        data["end"] = raw_end_date

    raw_gpa = get_resolved_field(
        education_instance, overrides, "gpa", education_instance.gpa
    )
    data["gpa"] = str(raw_gpa) if raw_gpa is not None else None

    if not is_resume_context and include_bullets_if_no_override:
        # Assuming education_instance.bullets relationship is ordered by BulletPoint.order_index
        data["bullets"] = [b.content for b in education_instance.bullets]

    return data


# --- CRUD Functions for Education ---


def create_education(user_id, data):
    """Creates a new education entry for a user."""
    user = User.query.get_or_404(user_id)  # Ensure user exists
    try:
        education = Education(
            user_id=user.id,
            school=data["school"],
            degree=data.get(
                "degree"
            ),  # Assuming 'degree' is a field in your Education model
            major=data.get(
                "major"
            ),  # Assuming 'major' is a field in your Education model
            start=data.get("start_date"),
            end=data.get("end_date"),
            gpa=data.get("gpa"),
            desc_long=data.get("desc_long"),
        )
        db.session.add(education)
        db.session.commit()

        # Handle bullets if provided
        if "bullets" in data and isinstance(data["bullets"], list):
            for idx, bullet_content in enumerate(data["bullets"]):
                bullet = BulletPoint(
                    parent_id=education.id,
                    parent_type=ParentType.education,
                    order_index=idx,
                    content=bullet_content,
                )
                db.session.add(bullet)
            db.session.commit()  # Commit bullets

        return serialize_education(education, include_bullets_if_no_override=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating education: {str(e)}")
    except KeyError as e:
        db.session.rollback()
        raise ValueError(f"Missing field for education creation: {str(e)}")


def get_education(education_id, include_bullets=False):
    """Retrieves a specific education entry."""
    education = Education.query.options(
        joinedload(Education.bullets) if include_bullets else []
    ).get_or_404(education_id)
    return serialize_education(
        education, include_bullets_if_no_override=include_bullets
    )


def get_all_educations_for_user(user_id, include_bullets=False):
    """Retrieves all education entries for a given user."""
    user = User.query.get_or_404(user_id)
    # Eager load bullets if requested
    query_options = [joinedload(Education.bullets)] if include_bullets else []
    educations = (
        Education.query.options(*query_options).filter_by(user_id=user_id).all()
    )
    return [
        serialize_education(edu, include_bullets_if_no_override=include_bullets)
        for edu in educations
    ]


def update_education(education_id, data):
    """Updates an existing education entry."""
    education = Education.query.options(joinedload(Education.bullets)).get_or_404(
        education_id
    )
    try:
        if "school" in data:
            education.school = data["school"]
        if "degree" in data:
            education.degree = data["degree"]
        if "major" in data:
            education.major = data["major"]
        if "start_date" in data:
            education.start = data["start_date"]
        if "end_date" in data:
            education.end = data["end_date"]
        if "gpa" in data:
            education.gpa = data["gpa"]
        if "desc_long" in data:
            education.desc_long = data["desc_long"]

        # More complex: Updating bullets (e.g., clear and re-add, or diff)
        # For simplicity, if 'bullets' are provided, we can replace them.
        if "bullets" in data and isinstance(data["bullets"], list):
            # Delete existing bullets for this education entry
            BulletPoint.query.filter_by(
                parent_id=education.id, parent_type=ParentType.education
            ).delete()
            # Add new bullets
            for idx, bullet_content in enumerate(data["bullets"]):
                bullet = BulletPoint(
                    parent_id=education.id,
                    parent_type=ParentType.education,
                    order_index=idx,
                    content=bullet_content,
                )
                db.session.add(bullet)

        db.session.commit()
        # Re-fetch to get updated bullets if they were changed
        updated_education = Education.query.options(joinedload(Education.bullets)).get(
            education_id
        )
        return serialize_education(
            updated_education, include_bullets_if_no_override=True
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error updating education: {str(e)}")


def delete_education(education_id):
    """Deletes an education entry."""
    education = Education.query.get_or_404(education_id)
    try:
        # Associated BulletPoints will be cascade deleted due to relationship setting
        db.session.delete(education)
        db.session.commit()
        return {"message": "Education entry deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error deleting education: {str(e)}")
