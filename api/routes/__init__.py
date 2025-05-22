from flask import Flask


def register_routes(app: Flask):
    """
    Registers all blueprints with the Flask application.
    """
    from .auth_routes import auth_routes
    from .user_routes import user_routes

    # from .website_routes import website_routes # Removed
    from .education_routes import education_routes
    from .experience_routes import experience_routes
    from .project_routes import project_routes
    from .skill_routes import skill_routes

    # from .bullet_point_routes import bullet_point_routes # Removed
    from .template_routes import template_routes
    from .resume_routes import resume_routes

    app.register_blueprint(auth_routes)
    app.register_blueprint(user_routes)
    # app.register_blueprint(website_routes) # Removed
    app.register_blueprint(education_routes)
    app.register_blueprint(experience_routes)
    app.register_blueprint(project_routes)
    app.register_blueprint(skill_routes)
    # app.register_blueprint(bullet_point_routes) # Removed
    app.register_blueprint(template_routes)
    app.register_blueprint(resume_routes)
