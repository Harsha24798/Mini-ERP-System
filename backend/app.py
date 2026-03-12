"""
Mini ERP System - Flask Application
Main application entry point
"""

from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, jwt, cors


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
    cors.init_app(app)

    # Configure JWT callbacks
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        """Callback to convert user_id to identity for JWT"""
        return str(user_id)  # Ensure ID is string for JWT

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Callback to load user from JWT"""
        from models import User

        identity = jwt_data["sub"]
        user_id = int(identity)  # Convert string back to int
        return User.query.filter_by(id=user_id).one_or_none()

    # Import models to ensure they are registered with SQLAlchemy
    with app.app_context():
        from models import (
            User,
            Role,
            Permission,
            Category,
            Product,
            Warehouse,
            Stock,
            StockMovement,
            Customer,
            SalesOrder,
            SalesOrderItem,
            Invoice,
            Payment,
            Supplier,
            PurchaseOrder,
            PurchaseOrderItem,
            Bill,
        )

    # Register blueprints
    from routes import register_blueprints

    register_blueprints(app)

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
