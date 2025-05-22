from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    from models.user import User

    db.metadata._add_table(User.__tablename__, None, User.__table__)
    db.init_app(app)
    with app.app_context():
        db.create_all()
