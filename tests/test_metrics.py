import sys
import os

app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
sys.path.insert(0, app_dir)

import pytest
from fastapi.testclient import TestClient
from main import app

def test_list_metrics_empty(test_client):
    """Test listing metrics when no data exists"""
    response = test_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_list_metrics_with_data(test_client):
    """Test listing metrics after ingesting data"""
    sample_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "temperature",
                "value": 23.5
            },
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "event",
                "value": "machine_start"
            }
        ]
    }
    test_client.post("/ingest", json=sample_data)
    
    response = test_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    
    metric_names = [metric["name"] for metric in data]
    assert "temperature" in metric_names
    assert "event" in metric_names
    
    for metric in data:
        assert "name" in metric
        assert "first_seen" in metric
        assert "value_type" in metric
        assert metric["value_type"] in ["number", "string"]

def test_metrics_value_types(test_client):
    """Test that value types are correctly identified"""
    test_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "numeric_metric",
                "value": 42.5
            },
            {
                "time": "2024-01-15T10:01:00Z",
                "metric": "string_metric",
                "value": "text_value"
            }
        ]
    }
    test_client.post("/ingest", json=test_data)
    
    response = test_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    
    metric_dict = {metric["name"]: metric for metric in data}
    assert metric_dict["numeric_metric"]["value_type"] == "number"
    assert metric_dict["string_metric"]["value_type"] == "string"