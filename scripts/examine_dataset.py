#!/usr/bin/env python3
import pandas as pd

def examine_dataset():
    """Examine the structure of the downloaded dataset"""
   
    csv_file = "data/iot_telemetry_data.csv"

    try:
        df = pd.read_csv(csv_file)
        print(f"\n Dataset Info:")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        
        print(f"\nColumns:")
        for col in df.columns:
            print(f"   - {col}")
        
        print(f"\nSample data:")
        print(df.head(3))
        
        print(f"\nData types:")
        print(df.dtypes)
        
        print(f"\nDate range (if timestamp column exists):")
        if 'timestamp' in df.columns:
            print(f"   From: {df['timestamp'].min()}")
            print(f"   To: {df['timestamp'].max()}")
        elif 'date' in df.columns:
            print(f"   From: {df['date'].min()}")
            print(f"   To: {df['date'].max()}")
            
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    examine_dataset()