from typing import override, List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from flask_login import UserMixin

from models import Base

from db import db

if TYPE_CHECKING:  # Avoid circular import
    from models.resume import Resume


class User(UserMixin, db.Model, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # https://stackoverflow.com/questions/6872310/whats-the-best-column-type-for-google-user-id
    google_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    profile_picture: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    linkedin: Mapped[str | None] = mapped_column(nullable=True)
    github: Mapped[str | None] = mapped_column(nullable=True)
    website: Mapped[str | None] = mapped_column(nullable=True)

    resumes: Mapped[List["Resume"]] = relationship(back_populates="user")

    @override
    def json(self):
        return {
            "id": self.id,
            "google_id": self.google_id,
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "website": self.website,
        }
