"""
Configuration for pytest and test fixtures
"""

import pytest
from app import create_app
from extensions import db
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create database session for testing - clean slate for each test"""
    with app.app_context():
        # Create tables before each test
        db.create_all()
        
        yield db.session
        
        # Clean up after each test
        db.session.remove()
        db.drop_all()
