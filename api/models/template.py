from typing import override

from sqlalchemy.orm import Mapped, mapped_column

from models import Base

from db import db


class Template(db.Model, Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    uri: Mapped[str] = mapped_column(nullable=False)  # GCS link to LaTeX template

    @override
    def json(self):
        return {"id": self.id, "name": self.name, "uri": self.uri}
