from sqlalchemy import select

from models.template import Template

from db import db


def get_all_templates(limit: int = 100) -> list[dict[str, any]]:
    stmt = select(Template).limit(limit)
    query = db.session.execute(stmt)
    templates = query.scalars().all()
    return [template.json() for template in templates]


def get_template(id: int) -> dict[str, any] | None:
    stmt = select(Template).where(Template.id == id)
    query = db.session.execute(stmt)
    template = query.scalar()
    return template.json() if template else None


def validate_template(args: dict[str, str] | None) -> bool:
    """
    Validate request JSON contains all required
    values for a template.
    """
    if args is None:
        return False
    return args.get("name") is not None


def create_template(name: str) -> Template:
    template = Template(name=name, uri="")
    template.save_to_db()

    return template


def update_template(id: int, name: str) -> bool:
    stmt = select(Template).where(Template.id == id)
    query = db.session.execute(stmt)
    template = query.scalar()

    if not template:
        return False

    template.name = name

    template.save_to_db()

    return True


def delete_template(id: int) -> bool:
    stmt = select(Template).where(Template.id == id)
    query = db.session.execute(stmt)
    template = query.scalar()

    if not template:
        return False

    template.delete_from_db()

    return True
