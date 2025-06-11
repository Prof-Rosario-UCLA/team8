import os

from flask import Blueprint

from flask_login import login_required, current_user
from db import db

from controllers.resume import get_full_resume
from controllers.template import get_template

from models.user import User
import requests

compile_views = Blueprint("compile_views", __name__, url_prefix="/compile")

TEXIFY_URL = os.environ.get("TEXIFY_URL") or "http://texify:8080"


@compile_views.post("/<int:resume_id>")
@login_required
def compile_resume(resume_id: int):
    assert isinstance(current_user, User)
    result = get_full_resume(resume_id, user=current_user, db_session=db.session)
    if not result:
        return {"error": "Resume not found"}, 404


    # TODO: for future support of custom templates
    # template_id = result.template_id
    # template = get_template(template_id)
    # if not template:
    #     return {"error": "Template not found"}, 404

    r = requests.post(
        TEXIFY_URL + "/compile",
        json={
            "template": " ", # TODO: for future support of custom templates, non-empty so not falsey
            "data": result.json(),
        },
    )

    return r.json()


@compile_views.get("/status/<job_id>")
@login_required
def check_status(job_id: str):
    r = requests.get(TEXIFY_URL + "/status/" + job_id)

    return r.json()
