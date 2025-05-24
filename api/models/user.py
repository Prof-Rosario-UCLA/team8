from typing import override

from sqlalchemy.orm import Mapped, mapped_column

from flask_login import UserMixin

from models import Base

from db import db


class User(UserMixin, db.Model, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # https://stackoverflow.com/questions/6872310/whats-the-best-column-type-for-google-user-id
    google_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    profile_picture: Mapped[str] = mapped_column(nullable=False)

    @override
    def json(self):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
        }
