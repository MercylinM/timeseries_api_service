import sys
import os

app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
sys.path.insert(0, app_dir)

import pytest
from fastapi.testclient import TestClient
from main import app

def test_query_existing_metric(test_client, clean_db):
    """Test querying an existing metric"""
    sample_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "temperature",
                "value": 23.5
            },
            {
                "time": "2024-01-15T10:05:00Z",
                "metric": "temperature",
                "value": 24.1
            }
        ]
    }
    response = test_client.post("/ingest", json=sample_data)
    assert response.status_code == 200
    
    query_data = {
        "metric": "temperature",
        "start_time": "2024-01-15T09:00:00Z",
        "end_time": "2024-01-15T11:00:00Z"
    }
    response = test_client.post("/query", json=query_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  

    values = [point['value'] for point in data]
    assert 23.5 in values
    assert 24.1 in values

def test_query_nonexistent_metric(test_client, clean_db):
    """Test querying a metric that doesn't exist"""
    query_data = {
        "metric": "nonexistent_metric",
        "start_time": "2024-01-15T09:00:00Z",
        "end_time": "2024-01-15T11:00:00Z"
    }
    response = test_client.post("/query", json=query_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_query_with_aggregation(test_client, clean_db):
    """Test querying with aggregation"""
    sample_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "temperature",
                "value": 23.5
            },
            {
                "time": "2024-01-15T10:30:00Z",
                "metric": "temperature",
                "value": 24.1
            },
            {
                "time": "2024-01-15T11:00:00Z", 
                "metric": "temperature", 
                "value": 25.0
            }
        ]
    }
    response = test_client.post("/ingest", json=sample_data)
    assert response.status_code == 200
    
    query_data = {
        "metric": "temperature",
        "start_time": "2024-01-15T09:00:00Z",
        "end_time": "2024-01-15T11:00:00Z",
        "aggregation": "avg",
        "interval": "1 hour"
    }
    response = test_client.post("/query", json=query_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all('value' in point for point in data)

def test_query_string_metric_aggregation(test_client, clean_db):
    """Test that string metrics cannot be aggregated"""
    string_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "event",
                "value": "start"
            }
        ]
    }
    response = test_client.post("/ingest", json=string_data)
    assert response.status_code == 200
    
    query_data = {
        "metric": "event",
        "start_time": "2024-01-15T09:00:00Z",
        "end_time": "2024-01-15T11:00:00Z",
        "aggregation": "avg",  
        "interval": "1 hour"
    }
    response = test_client.post("/query", json=query_data)
    assert response.status_code == 400
    assert "only supported for numeric metrics" in response.json()["detail"].lower()

def test_query_invalid_time_range(test_client, clean_db):
    """Test querying with invalid time range"""
    sample_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "temperature",
                "value": 23.5
            }
        ]
    }
    response = test_client.post("/ingest", json=sample_data)
    assert response.status_code == 200
    
    query_data = {
        "metric": "temperature",
        "start_time": "2024-01-15T11:00:00Z", 
        "end_time": "2024-01-15T09:00:00Z"    
    }
    response = test_client.post("/query", json=query_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0 

def test_query_all_aggregation_functions(test_client, clean_db):
    """Test all aggregation functions"""
    sample_data = {
        "data": [
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "temperature",
                "value": 23.5
            },
            {
                "time": "2024-01-15T10:30:00Z",
                "metric": "temperature",
                "value": 24.1
            }
        ]
    }
    response = test_client.post("/ingest", json=sample_data)
    assert response.status_code == 200
    
    aggregations = ["avg", "sum", "min", "max", "count"]
    
    for agg in aggregations:
        query_data = {
            "metric": "temperature",
            "start_time": "2024-01-15T09:00:00Z",
            "end_time": "2024-01-15T11:00:00Z",
            "aggregation": agg,
            "interval": "1 hour"
        }
        response = test_client.post("/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0