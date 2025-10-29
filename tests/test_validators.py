import pytest
from datetime import datetime, timedelta
from app.utils.validators import validate_timestamp, validate_metric_name, validate_data_points, validate_query_time_range
from app.models import DataPoint
from fastapi import HTTPException

def test_validate_timestamp():
    """Test timestamp validation"""
    past_time = datetime.now() - timedelta(hours=1)
    validate_timestamp(past_time) 
    
    future_time = datetime.now() + timedelta(hours=1)
    with pytest.raises(HTTPException) as exc_info:
        validate_timestamp(future_time)
    assert exc_info.value.status_code == 400
    assert "future" in exc_info.value.detail.lower()

def test_validate_metric_name():
    """Test metric name validation"""
    validate_metric_name("valid_metric") 
    
    with pytest.raises(HTTPException) as exc_info:
        validate_metric_name("")
    assert exc_info.value.status_code == 400
    
    with pytest.raises(HTTPException) as exc_info:
        validate_metric_name("   ")
    assert exc_info.value.status_code == 400

def test_validate_data_points():
    """Test data points validation"""
    valid_points = [
        DataPoint(time=datetime.now(), metric="test", value=1.0),
        DataPoint(time=datetime.now(), metric="test2", value="string")
    ]
    validate_data_points(valid_points) 
    
    with pytest.raises(HTTPException) as exc_info:
        validate_data_points([])
    assert exc_info.value.status_code == 400
    assert "no data points" in exc_info.value.detail.lower()

def test_validate_query_time_range():
    """Test query time range validation"""
    start = datetime.now() - timedelta(hours=1)
    end = datetime.now()
    validate_query_time_range(start, end) 
    
    with pytest.raises(HTTPException) as exc_info:
        validate_query_time_range(end, start)
    assert exc_info.value.status_code == 400
    assert "before" in exc_info.value.detail.lower()
    
    very_old = datetime.now() - timedelta(days=400)  
    with pytest.raises(HTTPException) as exc_info:
        validate_query_time_range(very_old, end)
    assert exc_info.value.status_code == 400
    assert "exceed" in exc_info.value.detail.lower()