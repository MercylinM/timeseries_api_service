import sys
import os
import pytest
import psycopg2

app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
sys.path.insert(0, app_dir)

from database import get_db_connection

def test_database_connection():
    """Test that the database connection works and can execute a simple query."""
    try:
        with get_db_connection() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test_val")
            result = cursor.fetchone()
            assert result['test_val'] == 1
    except psycopg2.OperationalError as e:
        pytest.fail(f"Database connection failed: {e}. Ensure your PostgreSQL server is running and accessible.")

def test_timescaledb_extension_exists():
    """
    Test that the TimescaleDB extension is installed in the database.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM pg_extension WHERE extname = 'timescaledb';
        """)
        result = cursor.fetchone()
        assert result is not None, "TimescaleDB extension is not installed. Please check your database setup."

def test_database_initialization():
    """Test that the database has the required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('metrics', 'time_series_data')
        """)
        tables = cursor.fetchall()
        table_names = [table['table_name'] for table in tables]
        
        assert 'metrics' in table_names, "Metrics table was not created."
        assert 'time_series_data' in table_names, "Time-series data table was not created."

def test_database_indexes():
    """Test that required indexes are created."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' AND indexname LIKE 'idx_%'
        """)
        indexes = cursor.fetchall()
        index_names = [index['indexname'] for index in indexes]
        
        assert 'idx_time_series_data_metric_time' in index_names, "Required index on (metric_id, time) was not created."
        
        print(f"Found indexes: {index_names}")

def test_hypertable_creation():
    """
    Test that the time_series_data table is correctly converted into a TimescaleDB hypertable.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM timescaledb_information.hypertable
            WHERE table_schema = 'public'
        """)
        hypertables = cursor.fetchall()
        hypertable_names = [ht['table_name'] for ht in hypertables]
        
        assert 'time_series_data' in hypertable_names, "time_series_data table was not found as a hypertable in the catalog."
        
        print(f"Found hypertables: {hypertable_names}")

