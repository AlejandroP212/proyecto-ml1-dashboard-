"""NASA FIRMS client.

Simulates NASA FIRMS (Fire Information for Resource Management System) data.
Provides thermal anomaly counts and average Fire Radiative Power (FRP) as a 
contextual feature for conflict intensity.
"""

import os
import pandas as pd
import numpy as np
from datetime import date, timedelta
from pathlib import Path

TARGET_COUNTRIES = ["IRN", "ISR", "USA"]

def generate_synthetic_firms(start_date: date, end_date: date, output_dir: Path):
    print(f"Generando datos FIRMS sintéticos desde {start_date} hasta {end_date}...")
    
    dates = []
    d = start_date
    while d <= end_date:
        dates.append(d)
        d += timedelta(days=1)
        
    records = []
    
    for current_date in dates:
        for country in TARGET_COUNTRIES:
            # FIRMS data makes more sense for IRN/ISR region in this context
            if country in ["IRN", "ISR"]:
                hotspots = max(0, int(np.random.normal(5, 3)))
                if hotspots > 0:
                    frp = np.random.uniform(10.0, 150.0)
                else:
                    frp = 0.0
            else:
                hotspots = 0
                frp = 0.0
                
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "country": country,
                "n_hotspots": hotspots,
                "avg_frp": round(frp, 2)
            })
            
    df = pd.DataFrame(records)
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = output_dir / "firms_aggregated.parquet"
    df.to_parquet(output_path, index=False)
    print(f"✓ Guardado en {output_path} ({len(df)} registros)")
    return df

if __name__ == "__main__":
    np.random.seed(45)
    output_dir = Path("data/raw/firms")
    start = date(2024, 1, 1)
    end = date(2026, 5, 8)
    generate_synthetic_firms(start, end, output_dir)
