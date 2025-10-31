from fastapi import APIRouter, HTTPException, Request 
from typing import List
import psycopg2
from models import QueryRequest, QueryResponse, AggregationFunction
from database import get_db_connection
from main import limiter 

router = APIRouter(prefix="/query", tags=["query"])

ALLOWED_INTERVALS = {
    '1 second', '5 seconds', '10 seconds', '30 seconds',
    '1 minute', '5 minutes', '10 minutes', '30 minutes',
    '1 hour', '2 hours', '6 hours', '12 hours',
    '1 day', '7 days', '1 month'
}

@router.post("", response_model=List[QueryResponse])
@limiter.limit("200/minute") 
async def query_data(request: Request, query_request: QueryRequest) -> List[QueryResponse]: 
    """
    Query time-series data with optional aggregation
    
    Rate Limited: 200 requests per minute per IP address
    
    Example payload:
    {
      "metric": "temperature",
      "start_time": "2024-01-15T00:00:00Z", 
      "end_time": "2024-01-15T23:59:59Z",
      "aggregation": "avg",
      "interval": "1 hour"
    }
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, value_type FROM metrics WHERE name = %s', (query_request.metric,))
            metric_result = cursor.fetchone()
            
            if not metric_result:
                raise HTTPException(status_code=404, detail=f"Metric '{query_request.metric}' not found")
            
            metric_id = metric_result['id']
            value_type = metric_result['value_type']
            
            if query_request.aggregation and query_request.interval:
                if query_request.interval not in ALLOWED_INTERVALS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid interval. Allowed intervals: {sorted(list(ALLOWED_INTERVALS))}"
                    )

                if value_type == 'string':
                    raise HTTPException(
                        status_code=400, 
                        detail="Aggregation is only supported for numeric metrics"
                    )
                
                aggregation_query = get_aggregation_query(query_request.aggregation, query_request.interval)
                cursor.execute(aggregation_query, (metric_id, query_request.start_time, query_request.end_time))
                
            else:
                cursor.execute('''
                    SELECT time, value, text_value
                    FROM time_series_data
                    WHERE metric_id = %s AND time BETWEEN %s AND %s
                    ORDER BY time
                ''', (metric_id, query_request.start_time, query_request.end_time))
            
            results = cursor.fetchall()
            
            response_data = []
            for row in results:
                row_dict = dict(row)
                if 'bucket' in row_dict: 
                    response_data.append(QueryResponse(
                        time=row_dict['bucket'],
                        value=row_dict['value']
                    ))
                else:
                    value = row_dict['text_value'] if row_dict['text_value'] is not None else row_dict['value']
                    response_data.append(QueryResponse(
                        time=row_dict['time'],
                        value=value
                    ))
            
            return response_data
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_aggregation_query(aggregation: AggregationFunction, interval: str) -> str:
    """Generate SQL query for different aggregation types using TimescaleDB's time_bucket function"""
    
    base_query = f'''
        SELECT 
            time_bucket('{interval}', time) as bucket,
            {{agg_function}}(value) as value
        FROM time_series_data
        WHERE metric_id = %s AND time BETWEEN %s AND %s
        GROUP BY bucket
        ORDER BY bucket
    '''

    if aggregation == AggregationFunction.AVG:
        return base_query.format(agg_function='AVG')
    elif aggregation == AggregationFunction.SUM:
        return base_query.format(agg_function='SUM')
    elif aggregation == AggregationFunction.MIN:
        return base_query.format(agg_function='MIN')
    elif aggregation == AggregationFunction.MAX:
        return base_query.format(agg_function='MAX')
    elif aggregation == AggregationFunction.COUNT:
        return f'''
            SELECT 
                time_bucket('{interval}', time) as bucket,
                COUNT(*) as value
            FROM time_series_data
            WHERE metric_id = %s AND time BETWEEN %s AND %s
            GROUP BY bucket
            ORDER BY bucket
        '''