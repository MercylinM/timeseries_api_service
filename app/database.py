import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from typing import Generator
import os
import dotenv
dotenv.load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    conn.cursor_factory = psycopg2.extras.RealDictCursor
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Enable TimescaleDB extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                value_type VARCHAR(20) NOT NULL CHECK (value_type IN ('number', 'string'))
            )
        ''')
        
        # Create time series data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_series_data (
                time TIMESTAMPTZ NOT NULL,
                metric_id INTEGER NOT NULL,
                value DOUBLE PRECISION,
                text_value TEXT,
                CHECK ( (value IS NULL) != (text_value IS NULL) ),
                FOREIGN KEY (metric_id) REFERENCES metrics (id)
            )
        ''')
        
        # Convert to TimescaleDB hypertable
        cursor.execute("SELECT create_hypertable('time_series_data', 'time', if_not_exists => TRUE);")
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_time_series_data_metric_time 
            ON time_series_data (metric_id, time DESC)
        ''')
        
        conn.commit()
    print("Database initialized successfully!")