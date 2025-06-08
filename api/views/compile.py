# from flask import Blueprint

# from flask_login import login_required, current_user

# from sqlalchemy import select, and_, func, delete

# from models.resume import Resume, ResumeSection, ResumeItem, ResumeAssociation

# from db import db

# import requests

# compile_view = Blueprint("compile_view", __name__, url_prefix="/compile")

# TEXIFY_URL = "http://localhost:9090"

# @compile_view.post('/<int:resume_id>')
# @login_required
# def compile_resume(resume_id: int):
#     stmt = select(Resume).where(and_(Resume.user_id == current_user.id, Resume.id == id))
#     result = db.session.execute(stmt)
#     result = result.scalar()
#     if not result:
#         return {"error": "Resume not found"}, 404

#     r = requests.post(TEXIFY_URL + "/")