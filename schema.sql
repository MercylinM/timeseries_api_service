-- 1. Enable the TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 2. Create the metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    value_type VARCHAR(20) NOT NULL CHECK (
        value_type IN ('number', 'string')
    )
);

-- 3. Create the time_series_data table
CREATE TABLE IF NOT EXISTS time_series_data (
    time TIMESTAMPTZ NOT NULL,
    metric_id INTEGER NOT NULL,
    value DOUBLE PRECISION,
    text_value TEXT,
    CHECK (
        (value IS NULL) != (text_value IS NULL)
    ),
    FOREIGN KEY (metric_id) REFERENCES metrics (id) ON DELETE CASCADE
);

-- 4. Convert the time_series_data table into a TimescaleDB hypertable
SELECT create_hypertable (
        'time_series_data', 'time', if_not_exists = > TRUE
    );

-- 5. Create indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_time_series_data_metric_time ON time_series_data (metric_id, time DESC);

-- 6. Add an index on the metric name for faster lookups during ingestion
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics (name);