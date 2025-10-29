from http.client import HTTPException
from fastapi import APIRouter, Request  
from typing import List
from models import MetricInfo
from database import get_db_connection
from main import limiter
import psycopg2

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("", response_model=List[MetricInfo])
@limiter.limit("100/minute") 
async def list_metrics(request: Request) -> List[MetricInfo]: 
    """
    List all available metrics with metadata
    
    Rate Limited: 100 requests per minute per IP address
    
    Returns:
    [
      {
        "name": "temperature",
        "first_seen": "2024-01-15T10:30:00Z",
        "value_type": "number"
      }
    ]
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, first_seen, value_type 
                FROM metrics 
                ORDER BY name
            ''')
            results = cursor.fetchall()
            
            return [
                MetricInfo(
                    name=row['name'],
                    first_seen=row['first_seen'],
                    value_type=row['value_type']
                )
                for row in results
            ]
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")