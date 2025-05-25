from flask_login import current_user

from sqlalchemy import select

from models.resume import Resume, ResumeSection, ResumeItem, ResumeAssociation

from db import db


# TODO(bliutech): refactor core logic from views/resume.py into here
