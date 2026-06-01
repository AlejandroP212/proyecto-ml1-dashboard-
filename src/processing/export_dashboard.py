"""Export data to JSON for the dashboard."""

import os
import json
import pandas as pd
from pathlib import Path

def export_dashboard_data():
    features_path = Path("data/final/features.parquet")
    metrics_path = Path("reports/cv_results.json")
    
    dashboard_data_dir = Path("dashboard/public/data")
    os.makedirs(dashboard_data_dir, exist_ok=True)
    
    if not features_path.exists():
        print(f"Error: {features_path} no existe")
        return
        
    df = pd.read_parquet(features_path)
    
    # Timeline data
    # Aggregate by date across all countries for overall intensity
    daily_overall = df.groupby('date')['escalation_level'].mean().reset_index()
    daily_overall.columns = ['date', 'overall_intensity']
    
    # Also export the full dataset as a list of dicts
    # Sort by date
    df_sorted = df.sort_values(by=['date', 'country'])
    
    features_json = df_sorted.to_dict(orient='records')
    with open(dashboard_data_dir / "features.json", "w") as f:
        json.dump(features_json, f)
        
    overall_json = daily_overall.to_dict(orient='records')
    with open(dashboard_data_dir / "overall_intensity.json", "w") as f:
        json.dump(overall_json, f)
        
    # Copy metrics if they exist
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        with open(dashboard_data_dir / "metrics.json", "w") as f:
            json.dump(metrics, f)
            
    print(f"Datos exportados a {dashboard_data_dir}")

if __name__ == "__main__":
    export_dashboard_data()
