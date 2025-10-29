#!/usr/bin/env python3
import requests
import time
import statistics
from datetime import datetime, timedelta

def performance_test(base_url="http://localhost:8000"):
    """
    Test API performance with real IoT data
    """
    print("API Performance Testing")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Raw temperature data (1 day)",
            "query": {
                "metric": "temperature",
                "start_time": "2020-07-12T00:00:00Z",
                "end_time": "2020-07-13T00:00:00Z"
            }
        },
        {
            "name": "Hourly averages (1 week)",
            "query": {
                "metric": "temperature", 
                "start_time": "2020-07-12T00:00:00Z",
                "end_time": "2020-07-19T00:00:00Z",
                "aggregation": "avg",
                "interval": "1 hour"
            }
        },
        {
            "name": "Multiple metrics query",
            "query": {
                "metric": "humidity",
                "start_time": "2020-07-12T00:00:00Z", 
                "end_time": "2020-07-13T00:00:00Z"
            }
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        response_times = []
        
        # First call (uncached)
        start_time = time.time()
        response = requests.post(f"{base_url}/query", json=test_case['query'])
        first_call_time = time.time() - start_time
        response_times.append(first_call_time)
        
        # Subsequent calls (cached)
        for i in range(4):
            start_time = time.time()
            response = requests.post(f"{base_url}/query", json=test_case['query'])
            call_time = time.time() - start_time
            response_times.append(call_time)
        
        results[test_case['name']] = {
            'first_call': first_call_time,
            'avg_cached': statistics.mean(response_times[1:]),
            'speedup': first_call_time / statistics.mean(response_times[1:]) if statistics.mean(response_times[1:]) > 0 else 0
        }
        
        print(f"   First call: {first_call_time:.3f}s")
        print(f"   Avg cached: {statistics.mean(response_times[1:]):.3f}s")
        print(f"   Speedup: {results[test_case['name']]['speedup']:.1f}x")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Data points returned: {len(data)}")
    
    print(f"\n Performance Summary:")
    print("=" * 30)
    for test_name, result in results.items():
        print(f"   {test_name}:")
        print(f"      First: {result['first_call']:.3f}s")
        print(f"      Cached: {result['avg_cached']:.3f}s") 
        print(f"      Speedup: {result['speedup']:.1f}x")
        print()

if __name__ == "__main__":
    performance_test()