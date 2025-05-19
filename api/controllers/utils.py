from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Optional, Dict
import datetime

def get_or_404(model, item_id, error_message_prefix="Item"):
    """
    Fetches an item from the database by its ID or raises ValueError if not found.
    This ValueError can then be caught in the route and turned into a 404.
    """
    item = model.query.get(item_id)
    if not item:
        raise ValueError(f"{error_message_prefix} with ID {item_id} not found.")
    return item

def get_resolved_field(instance: Any, overrides: Dict[str, Any], field_name: str, default_value: Any = None) -> Any:
    """
    Resolves a field's value by first checking the overrides dictionary,
    then falling back to an attribute on the instance.

    Args:
        instance: The model instance.
        overrides: The dictionary of overridden values.
        field_name: The name of the field/attribute to resolve.
        default_value: The value to return if the field is not in overrides
                       and not an attribute of the instance.

    Returns:
        The resolved value.
    """
    if field_name in overrides:
        return overrides[field_name]
    return getattr(instance, field_name, default_value)
