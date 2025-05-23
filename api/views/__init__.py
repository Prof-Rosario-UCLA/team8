from flask import Flask


def register_routes(app: Flask):
    """
    Registers all blueprints with the Flask application.
    """
    from .auth import auth_routes
    from .user import user_routes

    # from .bullet_point_routes import bullet_point_routes # Removed
    from .template import template_routes
    from .resume import resume_routes

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(template)
    app.register_blueprint(resume)
