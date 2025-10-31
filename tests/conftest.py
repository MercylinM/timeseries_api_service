import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app
from database import get_db_connection, init_db

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture(scope="function")
def clean_db():
    """
    Clean the database before each test function.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS time_series_data")
        cursor.execute("DROP TABLE IF EXISTS metrics")
        conn.commit()
    init_db()
    yield

@pytest.fixture(scope="function")
def sample_ingest_data():
    """Sample data for ingestion tests"""
    return {
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
            },
            {
                "time": "2024-01-15T10:00:00Z",
                "metric": "event",
                "value": "machine_start"
            }
        ]
    }

@pytest.fixture(scope="function")
def sample_query_data():
    """Sample data for query tests"""
    return {
        "metric": "temperature",
        "start_time": "2024-01-15T09:00:00Z",
        "end_time": "2024-01-15T11:00:00Z"
    }