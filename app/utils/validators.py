from fastapi import HTTPException
from datetime import datetime
from typing import List, Union
from models import DataPoint

def validate_timestamp(timestamp: datetime) -> None:
    """Validate that timestamp is not in the future"""
    if timestamp > datetime.now():
        raise HTTPException(
            status_code=400, 
            detail="Timestamp cannot be in the future"
        )

def validate_metric_name(metric_name: str) -> None:
    """Validate metric name format"""
    if not metric_name or not metric_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Metric name cannot be empty"
        )
    if len(metric_name) > 100:
        raise HTTPException(
            status_code=400,
            detail="Metric name too long (max 100 characters)"
        )
    
def validate_metric_value(value: Union[float, str], value_type: str):
    if value_type == 'number' and not isinstance(value, (int, float)):
        raise HTTPException(status_code=400, detail="Numeric metric requires number value")
    if value_type == 'string' and not isinstance(value, str):
        raise HTTPException(status_code=400, detail="String metric requires string value")

def validate_data_points(data_points: List[DataPoint]) -> None:
    """Validate a list of data points"""
    if not data_points:
        raise HTTPException(
            status_code=400,
            detail="No data points provided"
        )
    
    if len(data_points) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Too many data points in single request (max 1000)"
        )
    
    for point in data_points:
        validate_timestamp(point.time)
        validate_metric_name(point.metric)

def validate_query_time_range(start_time: datetime, end_time: datetime) -> None:
    """Validate query time range is reasonable"""
    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before end time"
        )
    
    time_range = end_time - start_time
    if time_range.days > 365:
        raise HTTPException(
            status_code=400,
            detail="Query time range cannot exceed 1 year"
        )

def validate_aggregation_interval(interval: str) -> None:
    """Validate aggregation interval format"""
    valid_intervals = ['1 minute', '5 minutes', '15 minutes', '1 hour', '6 hours', '1 day']
    if interval not in valid_intervals:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval. Must be one of: {', '.join(valid_intervals)}"
        )