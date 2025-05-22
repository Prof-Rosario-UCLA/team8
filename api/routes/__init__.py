from flask import Flask


def register_routes(app: Flask):
    """
    Registers all blueprints with the Flask application.
    """
    from .auth import auth_routes
    from .user import user_routes

    # from .website_routes import website_routes # Removed
    from .education import education_routes
    from .experience import experience_routes
    from .project import project_routes
    from .skill import skill_routes

    # from .bullet_point_routes import bullet_point_routes # Removed
    from .template import template_routes
    from .resume import resume_routes

    app.register_blueprint(auth)
    app.register_blueprint(user)
    # app.register_blueprint(website_routes) # Removed
    app.register_blueprint(education)
    app.register_blueprint(experience)
    app.register_blueprint(project)
    app.register_blueprint(skill)
    # app.register_blueprint(bullet_point_routes) # Removed
    app.register_blueprint(template)
    app.register_blueprint(resume)
