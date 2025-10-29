import pytest
from fastapi.testclient import TestClient

def test_cache_info_endpoint(test_client):
    """Test cache info endpoint"""
    response = test_client.get("/cache/info")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_clear_cache_endpoint(test_client):
    """Test cache clear endpoint"""
    response = test_client.post("/cache/clear")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "cleared" in data["message"].lower()

def test_clear_metric_cache_endpoint(test_client):
    """Test clearing cache for specific metric"""
    response = test_client.post("/cache/metrics/temperature/clear")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "temperature" in data["message"]

def test_list_cache_keys_endpoint(test_client):
    """Test listing cache keys"""
    response = test_client.get("/cache/keys")
    assert response.status_code in [200, 503]