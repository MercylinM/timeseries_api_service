import pytest
from datetime import datetime
from app.models import DataPoint, IngestRequest, QueryRequest, MetricInfo, QueryResponse, AggregationFunction

def test_data_point_model():
    """Test DataPoint model validation"""
    numeric_point = DataPoint(
        time=datetime.now(),
        metric="temperature",
        value=23.5
    )
    assert numeric_point.metric == "temperature"
    assert numeric_point.value == 23.5
    
    string_point = DataPoint(
        time=datetime.now(),
        metric="event",
        value="start"
    )
    assert string_point.metric == "event"
    assert string_point.value == "start"

def test_ingest_request_model():
    """Test IngestRequest model"""
    data_points = [
        DataPoint(time=datetime.now(), metric="test", value=1.0),
        DataPoint(time=datetime.now(), metric="test2", value="string")
    ]
    
    request = IngestRequest(data=data_points)
    assert len(request.data) == 2
    assert isinstance(request.data[0].value, float)
    assert isinstance(request.data[1].value, str)

def test_query_request_model():
    """Test QueryRequest model"""
    query = QueryRequest(
        metric="temperature",
        start_time=datetime.now(),
        end_time=datetime.now()
    )
    assert query.metric == "temperature"
    assert query.aggregation is None
    assert query.interval is None
    
    query_with_agg = QueryRequest(
        metric="temperature",
        start_time=datetime.now(),
        end_time=datetime.now(),
        aggregation=AggregationFunction.AVG,
        interval="1 hour"
    )
    assert query_with_agg.aggregation == AggregationFunction.AVG
    assert query_with_agg.interval == "1 hour"

def test_metric_info_model():
    """Test MetricInfo model"""
    metric = MetricInfo(
        name="test_metric",
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        value_type="number"
    )
    assert metric.name == "test_metric"
    assert metric.value_type == "number"

def test_query_response_model():
    """Test QueryResponse model"""
    response_num = QueryResponse(
        time=datetime.now(),
        value=42.5
    )
    assert response_num.value == 42.5
    
    response_str = QueryResponse(
        time=datetime.now(),
        value="status"
    )
    assert response_str.value == "status"

def test_aggregation_function_enum():
    """Test AggregationFunction enum"""
    assert AggregationFunction.AVG == "avg"
    assert AggregationFunction.SUM == "sum"
    assert AggregationFunction.MIN == "min"
    assert AggregationFunction.MAX == "max"
    assert AggregationFunction.COUNT == "count"