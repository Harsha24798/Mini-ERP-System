# Routes package
"""
API Routes
"""
from flask import Blueprint


def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    from routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
