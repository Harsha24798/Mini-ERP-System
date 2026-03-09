"""
Basic tests for application setup
"""

import pytest


def test_app_exists(app):
    """Test that app instance exists"""
    assert app is not None


def test_app_is_testing(app):
    """Test that app is in testing mode"""
    assert app.config["TESTING"] is True


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_index_endpoint(client):
    """Test index endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Mini ERP System API" in response.json["message"]


def test_404_error(client):
    """Test 404 error handler"""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    assert "error" in response.json
