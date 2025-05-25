from flask import Blueprint, request, jsonify

from flask_login import login_required

from controllers.template import (
    get_all_templates,
    get_template,
    validate_template,
    create_template,
    update_template,
    delete_template,
)

template_views = Blueprint("template_views", __name__, url_prefix="/template")


@template_views.get("/all")
@login_required
def handle_get_all_templates():
    return get_all_templates()


@template_views.get("/<int:id>")
@login_required
def handle_get_template(id: int):
    if not id:
        return {"error": "Missing id"}, 400

    template = get_template(id)
    if template:
        return template
    return {"error": "Template not found"}, 404


@template_views.post("/create")
@login_required
def handle_create_template():
    data = request.get_json()
    if not validate_template(data):
        return {"Missing data"}, 400

    template = create_template(data.get("name"))

    return {"message": f"Template (id = {template.id}) created"}


@template_views.put("/update/<int:id>")
@login_required
def handle_update_template(id: int):
    if not id:
        return {"error": "Missing id"}, 400

    data = request.get_json()
    if not validate_template(data):
        return {"Missing data"}, 400

    updated = update_template(id, data.get("name", ""))
    if not updated:
        return {"error": "Template not found"}, 404

    return {"message": f"Template (id = {id}) updated"}


@template_views.delete("/delete/<int:id>")
@login_required
def handle_delete_template(id: int):
    if not id:
        return {"error": "Missing id"}, 400

    deleted = delete_template(id)
    if not deleted:
        return {"error": "Template not found"}, 404

    return {"message": f"Template deleted"}
