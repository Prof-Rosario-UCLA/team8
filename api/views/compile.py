from flask import Blueprint

from flask_login import login_required, current_user

from sqlalchemy import select, and_, func, delete

from models.resume import Resume, ResumeSection, ResumeItem, ResumeAssociation

from controllers.resume import get_full_resume
from controllers.template import get_template

from db import db

import requests

compile_view = Blueprint("compile_view", __name__, url_prefix="/compile")

TEXIFY_URL = "http://localhost:9090"


@compile_view.post("/<int:resume_id>")
@login_required
def compile_resume(resume_id: int):
    result = get_full_resume(resume_id)
    if not result:
        return {"error": "Resume not found"}, 404

    template_id = result["template"]
    template = get_template(template_id)
    if not template:
        return {"error": "Template not found"}, 404

    r = requests.post(
        TEXIFY_URL + "/",
        json={
            "template": template.get("uri", ""),
            "data": result.json(),
        },
    )

    return r.json()


@compile_view.get("/status/<job_id>")
@login_required
def check_status(job_id: str):
    r = requests.get(TEXIFY_URL + "/" + job_id)
    return r.json()
