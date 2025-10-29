import sys
import os
import pytest

app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
sys.path.insert(0, app_dir)


from fastapi.testclient import TestClient
from main import app

def test_ingest_valid_data(test_client, sample_ingest_data):
    """Test ingesting valid data"""
    response = test_client.post("/ingest", json=sample_ingest_data)
    assert response.status_code == 200
    data = response.json()
    assert data["ingested_count"] == 3
    assert "Successfully ingested" in data["message"]

def test_ingest_empty_data(test_client):
    """Test ingesting empty data"""
    response = test_client.post("/ingest", json={"data": []})
    assert response.status_code in [200, 400]

def test_ingest_mixed_data_types(test_client):
    """Test ingesting mixed numeric and string data"""
    mixed_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "numeric_metric",
                "value": 42.5
            },
            {
                "time": "2024-01-15T10:01:00Z",
                "metric": "string_metric",
                "value": "status_update"
            }
        ]
    }
    response = test_client.post("/ingest", json=mixed_data)
    assert response.status_code == 200
    data = response.json()
    assert data["ingested_count"] == 2

def test_ingest_duplicate_metrics(test_client):
    """Test that duplicate metrics are handled correctly"""
    duplicate_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "duplicate_metric",
                "value": 1.0
            },
            {
                "time": "2024-01-15T10:01:00Z",
                "metric": "duplicate_metric",  
                "value": 2.0
            }
        ]
    }
    response = test_client.post("/ingest", json=duplicate_data)
    assert response.status_code == 200
    data = response.json()
    assert data["ingested_count"] == 2

def test_ingest_invalid_timestamp(test_client):
    """Test ingesting data with invalid timestamp"""
    invalid_data = {
        "data": [
            {
                "time": "invalid-timestamp",
                "metric": "test_metric",
                "value": 1.0
            }
        ]
    }
    response = test_client.post("/ingest", json=invalid_data)
    assert response.status_code == 422

def test_ingest_missing_required_fields(test_client):
    """Test ingesting data with missing required fields"""
    incomplete_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "value": 1.0
            }
        ]
    }
    response = test_client.post("/ingest", json=incomplete_data)
    assert response.status_code == 422 