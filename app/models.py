from pydantic import BaseModel
from datetime import datetime
from typing import Union, List, Optional
from enum import Enum

class AggregationFunction(str, Enum):
    AVG = "avg"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    COUNT = "count"

class DataPoint(BaseModel):
    time: datetime
    metric: str
    value: Union[float, str]

class IngestRequest(BaseModel):
    data: List[DataPoint]

class QueryRequest(BaseModel):
    metric: str
    start_time: datetime
    end_time: datetime
    aggregation: Optional[AggregationFunction] = None
    interval: Optional[str] = None

class MetricInfo(BaseModel):
    name: str
    first_seen: datetime
    value_type: str

class QueryResponse(BaseModel):
    time: datetime
    value: Union[float, str, None]