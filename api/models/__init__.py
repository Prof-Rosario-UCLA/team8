from abc import abstractmethod

from db import db


class Base:
    @abstractmethod
    def json(self) -> dict[str, str]:
        pass

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
