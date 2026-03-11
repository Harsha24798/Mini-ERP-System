"""
Flask extensions initialization
Centralized location for all Flask extensions to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions (without app binding)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
