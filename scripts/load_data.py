#!/usr/bin/env python3
import pandas as pd
import requests
import json
import os
import sys
from datetime import datetime
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def load_iot_dataset(csv_file_path, base_url="http://localhost:8000", batch_size=500, max_rows=None):
    """
    Load IoT sensor dataset into the Timeseries API
    """
    print(f" Loading IoT dataset from: {csv_file_path}")
    
    try:
        data_frame = pd.read_csv(csv_file_path)
        if max_rows:
            data_frame = data_frame.head(max_rows)
            
        print(f" Loaded {len(data_frame):,} records")
        print(f" Columns: {list(data_frame.columns)}")
        
        # Convert Unix timestamp to ISO format
        print(" Converting timestamps...")
        data_frame['timestamp_iso'] = pd.to_datetime(data_frame['ts'], unit='s').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        total_ingested = 0
        batch_count = 0
        
        for start_idx in range(0, len(data_frame), batch_size):
            end_idx = min(start_idx + batch_size, len(data_frame))
            batch_data_frame = data_frame.iloc[start_idx:end_idx]
            
            data_points = []
            
            for _, row in batch_data_frame.iterrows():
                timestamp = row['timestamp_iso']
                device_id = row['device']
                
                # Add device ID as a metric
                data_points.append({
                    "time": timestamp,
                    "metric": "device_id",
                    "value": device_id
                })
                
                # Add all numeric sensor readings
                numeric_metrics = {
                    'co': 'carbon_monoxide',
                    'humidity': 'humidity', 
                    'lpg': 'liquefied_petroleum_gas',
                    'smoke': 'smoke',
                    'temp': 'temperature'
                }
                
                for col_name, metric_name in numeric_metrics.items():
                    if pd.notna(row[col_name]):
                        data_points.append({
                            "time": timestamp,
                            "metric": metric_name,
                            "value": float(row[col_name])
                        })
                
                # Add boolean metrics
                boolean_metrics = {
                    'light': 'light_status',
                    'motion': 'motion_detected'
                }
                
                for col_name, metric_name in boolean_metrics.items():
                    if pd.notna(row[col_name]):
                        # Convert boolean to string or numeric
                        bool_value = 1 if row[col_name] else 0
                        data_points.append({
                            "time": timestamp,
                            "metric": metric_name,
                            "value": bool_value
                        })
            
            if data_points:
                # Send batch to API
                success = send_batch(data_points, base_url)
                if success:
                    total_ingested += len(data_points)
                    batch_count += 1
                    print(f" Batch {batch_count}: Ingested {len(data_points):,} data points (Total: {total_ingested:,})")
                else:
                    print(f" Batch {batch_count}: Failed to ingest")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        print(f"\n Completed! Total data points ingested: {total_ingested:,}")
        
        # Print summary
        print(f"\n Data Summary:")
        print(f"   - Device IDs: {len(data_frame['device'].unique())} unique devices")
        print(f"   - Time range: {data_frame['timestamp_iso'].min()} to {data_frame['timestamp_iso'].max()}")
        print(f"   - Metrics created: device_id, carbon_monoxide, humidity, liquefied_petroleum_gas, smoke, temperature, light_status, motion_detected")
        
        return total_ingested
        
    except Exception as e:
        print(f" Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return 0

def send_batch(data_points, base_url):
    """Send a batch of data points to the API"""
    payload = {"data": data_points}
    
    try:
        response = requests.post(f"{base_url}/ingest", json=payload, timeout=30)
        if response.status_code == 200:
            return True
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Load IoT sensor data into Timeseries API')
    parser.add_argument('--file', type=str, help='Path to CSV file', required=False)
    parser.add_argument('--url', type=str, default='http://localhost:8000', help='API base URL')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for ingestion')
    parser.add_argument('--max-rows', type=int, help='Maximum number of rows to process')
    
    args = parser.parse_args()
    
    if args.file:
        csv_file = args.file
    else:
             
        csv_file = 'data/iot_telemetry_data.csv'  
    
    if csv_file:
        load_iot_dataset(csv_file, args.url, args.batch_size, args.max_rows)
    else:
        print("Please specify the CSV file path")
