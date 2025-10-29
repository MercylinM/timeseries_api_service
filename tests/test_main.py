import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "redis_status" in data
    assert data["message"] == "Super-Simple Timeseries API Service"

def test_health_endpoint(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "redis" in data
    assert "database" in data
    assert data["status"] == "healthy"

def test_docs_endpoint(test_client):
    """Test that API documentation is available"""
    response = test_client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema(test_client):
    """Test that OpenAPI schema is available"""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema