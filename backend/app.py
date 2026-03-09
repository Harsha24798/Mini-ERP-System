"""
Mini ERP System - Flask Application
Main application entry point
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    """
    Application factory pattern
    Creates and configures the Flask application

    Args:
        config_class: Configuration class to use

    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints (will be added in later phases)
    # from routes.auth_routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring"""
        return (
            jsonify(
                {
                    "status": "healthy",
                    "message": "Mini ERP System API is running",
                    "version": "1.0.0",
                }
            ),
            200,
        )

    # Root endpoint
    @app.route("/", methods=["GET"])
    def index():
        """Root endpoint"""
        return (
            jsonify(
                {
                    "message": "Welcome to Mini ERP System API",
                    "version": "1.0.0",
                    "docs": "/api/docs",
                }
            ),
            200,
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
