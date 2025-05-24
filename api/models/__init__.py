from abc import abstractmethod

from db import db


class Base:
    @abstractmethod
    def json(self) -> dict[str, str]:
        pass

    # TODO(bliutech): add a mutex to db object
    # to make it thread safe or use SQLAlchemy
    # connection pool instead
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
