from fastapi import APIRouter, HTTPException, Request 
from typing import Dict, Any
import psycopg2
from models import IngestRequest
from database import get_db_connection
from main import limiter  

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("")
@limiter.limit("50/minute")  
async def ingest_data(request: Request, ingest_request: IngestRequest) -> Dict[str, Any]:
    """
    Ingest time-series data points
    
    Rate Limited: 50 requests per minute per IP address
    
    Example payload:
    {
      "data": [
        {
          "time": "2024-01-15T10:30:00Z",
          "metric": "temperature", 
          "value": 23.5
        },
        {
          "time": "2024-01-15T10:30:00Z",
          "metric": "event",
          "value": "machine_start"
        }
      ]
    }
    """
    inserted_count = 0
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for point in ingest_request.data:
            value_type = 'string' if isinstance(point.value, str) else 'number'
            
            try:
                cursor.execute('''
                    INSERT INTO metrics (name, value_type, last_seen) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        value_type = EXCLUDED.value_type,
                        last_seen = GREATEST(metrics.last_seen, EXCLUDED.last_seen)
                    RETURNING id;
                ''', (point.metric, value_type, point.time))
                
                metric_id = cursor.fetchone()['id']
                
                if value_type == 'number':
                    cursor.execute('''
                        INSERT INTO time_series_data (time, metric_id, value)
                        VALUES (%s, %s, %s)
                    ''', (point.time, metric_id, point.value))
                else:
                    cursor.execute('''
                        INSERT INTO time_series_data (time, metric_id, text_value)
                        VALUES (%s, %s, %s)
                    ''', (point.time, metric_id, point.value))
                
                inserted_count += 1
                
            except psycopg2.Error as e:
                print(f"Database error: {e}")
                conn.rollback() # Rollback the transaction on error
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        conn.commit()
    
    return {
        "message": f"Successfully ingested {inserted_count} data points",
        "ingested_count": inserted_count
    }