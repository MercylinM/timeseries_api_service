#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
import statistics

def analyze_iot_data(base_url="http://localhost:8000"):
    """
    Perform specialized analysis on the IoT sensor data
    """
    print(" Sensor Data Analysis")
    print("=" * 50)
    
    response = requests.get(f"{base_url}/metrics")
    if response.status_code != 200:
        print("Failed to get metrics")
        return
    
    metrics = response.json()
    
    print(f"Found {len(metrics)} metrics:")
    for metric in metrics:
        print(f"   - {metric['name']} ({metric['value_type']})")
    
    start_time = "2020-07-12T00:00:00Z"
    end_time = "2020-07-19T23:59:59Z" 
    
    print(f"\n Analyzing data from {start_time} to {end_time}")
    
    print(f"\n Device Analysis:")
    
    device_query = {
        "metric": "device_id",
        "start_time": start_time,
        "end_time": end_time
    }
    
    response = requests.post(f"{base_url}/query", json=device_query)
    if response.status_code == 200:
        device_data = response.json()
        unique_devices = set(point['value'] for point in device_data)
        print(f"   Found {len(unique_devices)} unique devices: {list(unique_devices)}")
    
    environmental_metrics = ['temperature', 'humidity', 'carbon_monoxide', 'smoke', 'liquefied_petroleum_gas']
    
    for metric_name in environmental_metrics:
        if any(m['name'] == metric_name for m in metrics):
            print(f"\n  {metric_name.replace('_', ' ').title()} Analysis:")
            
            query_data = {
                "metric": metric_name,
                "start_time": start_time,
                "end_time": end_time,
                "aggregation": "avg",
                "interval": "1 hour"
            }
            
            response = requests.post(f"{base_url}/query", json=query_data)
            if response.status_code == 200:
                data = response.json()
                if data:
                    values = [point['value'] for point in data if point['value'] is not None]
                    if values:
                        print(f"      Statistics:")
                        print(f"      Data points: {len(values)}")
                        print(f"      Average: {statistics.mean(values):.4f}")
                        print(f"      Min: {min(values):.4f}")
                        print(f"      Max: {max(values):.4f}")
                        
                        # Find anomalies (values > 2 standard deviations from mean)
                        if len(values) > 1:
                            mean_val = statistics.mean(values)
                            std_val = statistics.stdev(values)
                            anomalies = [v for v in values if abs(v - mean_val) > 2 * std_val]
                            if anomalies:
                                print(f"  Anomalies: {len(anomalies)} values outside 2σ")
    
    boolean_metrics = ['light_status', 'motion_detected']
    
    for metric_name in boolean_metrics:
        if any(m['name'] == metric_name for m in metrics):
            print(f"\n {metric_name.replace('_', ' ').title()} Analysis:")
            
            query_data = {
                "metric": metric_name,
                "start_time": start_time,
                "end_time": end_time,
                "aggregation": "sum",
                "interval": "1 day"
            }
            
            response = requests.post(f"{base_url}/query", json=query_data)
            if response.status_code == 200:
                data = response.json()
                if data:
                    active_periods = [point['value'] for point in data if point['value'] is not None]
                    if active_periods:
                        total_active = sum(active_periods)
                        print(f"   Total active periods: {total_active:.0f}")
                        
                        total_query = {
                            "metric": metric_name,
                            "start_time": start_time,
                            "end_time": end_time,
                            "aggregation": "count",
                            "interval": "1 day"
                        }
                        
                        response = requests.post(f"{base_url}/query", json=total_query)
                        if response.status_code == 200:
                            count_data = response.json()
                            total_readings = sum(point['value'] for point in count_data if point['value'] is not None)
                            if total_readings > 0:
                                active_percentage = (total_active / total_readings) * 100
                                print(f"   Active percentage: {active_percentage:.1f}%")

if __name__ == "__main__":
    analyze_iot_data()