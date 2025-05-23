from sqlalchemy.orm import Mapped, mapped_column

from flask_login import UserMixin

from db import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # https://stackoverflow.com/questions/6872310/whats-the-best-column-type-for-google-user-id
    google_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    profile_picture: Mapped[str] = mapped_column(nullable=False)
