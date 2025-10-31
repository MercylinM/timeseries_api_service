# Super-Simple Timeseries API

A high-performance, time-series data storage and query service built with FastAPI, PostgreSQL, and the TimescaleDB extension. This service is designed to efficiently handle massive volumes of time-series data, making it ideal for IoT, monitoring, and analytics applications.

## Features

- **High-Performance Storage**: Leverages TimescaleDB for scalable and efficient ingestion of time-series data.
- **Flexible Querying**: Query raw data or apply powerful aggregation functions like AVG, SUM, MIN, MAX, COUNT, over custom time intervals.
- **Mixed Data Types**: Store both numeric and string-based data points within the same service.
- **Redis Caching**: Integrated Redis caching layer to significantly speed up frequent metric lookups.
- **API Endpoints**: Clean RESTful endpoints for ingesting, querying, and discovering metrics.
- **Interactive Documentation**: Auto-generated OpenAPI Swagger documentation for easy exploration and testing.
- **Docker Setup**: Fully containerized with Docker and orchestrated with Docker Compose for simple deployment.
- **Unit Testing**: Comprehensive test suite ensuring reliability and correctness.

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with TimescaleDB extension
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest
- **Data Validation**: Pydantic

## API Endpoints

- `POST /ingest` - Ingest a batch of time-series data points.
- `POST /query` - Query data for a specific metric, with optional aggregation and time-bucketing.
- `GET /metrics` - List all available metrics and their metadata.
- `GET /cache/info` - Get statistics and information from the Redis cache.

## Quick Start with Docker Compose

This project is designed to be run using Docker and Docker Compose, which manages all dependencies for you.

### Prerequisites

- [Docker](https://www.docker.com/get-started/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the Repository

```bash
git clone https://github.com/MercylinM/timeseries_api_service.git
cd timeseries_api_service
```

### 2. Start the Services

Run the following command to build the application image and start all services (API, PostgreSQL/TimescaleDB, and Redis) in the background:

```bash
docker-compose up --build -d
```

This command will:

- Pull the official TimescaleDB and Redis images.
- Build your FastAPI application image.
- Start all containers, configured to communicate with each other.
- Automatically initialize the database schema using the `schema.sql` file.

### 3. Access the API

Once the services are running, you can access:

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure

```
├── app/                         
│   ├── routes/                   
│   │   ├── cache.py              # Endpoint for cache statistics and management
│   │   ├── ingest.py             # Endpoint for ingesting time-series data
│   │   ├── metrics.py            # Endpoint for listing available metrics
│   │   └── query.py              # Endpoint for querying data with aggregation
│   ├── utils/                    
│   │   ├── cache.py              
│   │   └── validators.py         
│   ├── database.py               # Database connection and core logic
│   ├── main.py                   # FastAPI application entry point and configuration
│   └── models.py                 # Pydantic data models for request/response validation
├── tests/                        
│   ├── conftest.py     
│   ├── test_cache.py            
│   ├── test_database.py         
│   ├── test_ingest.py           
│   ├── test_main.py              
│   ├── test_metrics.py          
│   ├── test_models.py            
│   ├── test_query.py             
│   └── test_validators.py        
├── data/                         
│   └── iot_telemetry_data.csv    # Sample CSV file containing IoT sensor readings for testing and data loading
├── scripts/                      
│   ├── analyze_data.py           
│   ├── examine_dataset.py        
│   ├── load_data.py             
│   └── performance_test.py       
├── docker-compose.yml            
├── Dockerfile                    
├── requirements.txt              
├── schema.sql                    # Database schema initialization script for TimescaleDB
└── README.md                     
```

## Testing and Data Management

This project includes a comprehensive test suite and a set of helper scripts to demonstrate a full data workflow, from initial data exploration to loading and analysis.

### Test Suite (`tests/`)

The test suite is built with `pytest` and is designed to ensure the reliability and correctness of the API endpoints, database interactions, and utility functions.

To run the entire test suite, ensure the Docker containers are running and execute:

```bash
pytest
```

#### Test Files Overview

- `conftest.py`: Contains Pytest fixtures, such as `clean_db` to reset the database between tests and `sample_ingest_data` to provide test data.
- `test_database.py`: Validates the database schema, including table creation, indexes, and the TimescaleDB hypertable configuration.
- `test_ingest.py`: Tests the `/ingest` endpoint, including successful ingestion and error handling for invalid data.
- `test_query.py`: Tests the `/query` endpoint for both raw data retrieval and various aggregation functions.
- `test_metrics.py`: Tests the `/metrics` endpoint and the caching mechanism.
- `test_cache.py`: Specifically tests the Redis caching functionality.
- `test_models.py`: Validates the Pydantic models for request and response data.
- `test_validators.py`: Tests custom data validation logic.

### Helper Scripts (`scripts/`)

The `scripts/` directory contains a collection of Python scripts to help interact with the API and manage data.

#### Prerequisites for Running Scripts

Before running the scripts, make sure the API is running:

```bash
docker-compose up -d
```

You may also need to install the project's dependencies in the local environment if running the scripts outside of Docker:

```bash
pip install -r requirements.txt
```

#### Script Descriptions

1. **`examine_dataset.py`**
    - **Purpose**: To perform an initial inspection of the sample dataset before loading it. It helps understand the data's structure, columns, and content.
    - **Usage**:

        ```bash
        python scripts/examine_dataset.py
        ```

2. **`load_data.py`**
    - **Purpose**: To read the sample `iot_telemetry_data.csv` file and ingest its contents into the running API service via the `/ingest` endpoint.
    - **Usage**:

        ```bash
        python scripts/load_data.py --max-rows 10000 --batch-size 500
        ```

3. **`analyze_data.py`**
    - **Purpose**: To query the now-populated API to perform basic analysis. It demonstrates how to use the `/query` endpoint with aggregation to find insights like average sensor readings or event counts over time.
    - **Usage**:

        ```bash
        python scripts/analyze_data.py
        ```

4. **`performance_test.py`**
    - **Purpose**: To stress-test the API endpoints and measure their performance under load. This script simulates a high volume of requests to help identify bottlenecks and ensure the system can handle traffic.
    - **Usage**:

        ```bash
        python scripts/performance_test.py
        ```

### Sample Data (`data/`)

- **`iot_telemetry_data.csv`**: A sample CSV file containing mock IoT sensor data. It includes various metrics like temperature, pressure, and status events, along with timestamps. This file is used by `load_data.py` to populate the database.

## Development (Local Setup)

For local development, you can run the app without Docker Compose, but you must have PostgreSQL and TimescaleDB installed locally.

1. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Set up a local TimescaleDB instance** and create a database.

3. **Set Environment Variables**:

    ```bash
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_NAME="database_name"
    export DB_USER="user_name"
    export DB_PASSWORD="password"
    export REDIS_HOST="localhost"
    export REDIS_PORT="6379"
    ```

4. **Initialize the Database**:

    ```bash
    psql -U user_name -d database_name -f schema.sql
    ```

5. **Run the Application**:

    ```bash
    uvicorn main:app --reload
    ```

## License

This project is licensed under the MIT License.
