from ..models import db, BulletPoint, ParentType, Education, Experience, Project
from sqlalchemy.exc import SQLAlchemyError

def serialize_bullet_point(bullet: BulletPoint):
    """Converts a BulletPoint object to a dictionary."""
    return {
        'id': str(bullet.id),
        'parent_type': bullet.parent_type.value,
        'parent_id': str(bullet.parent_id),
        'order_index': bullet.order_index,
        'content': bullet.content
    }
