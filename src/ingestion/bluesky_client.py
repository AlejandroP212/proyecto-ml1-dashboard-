"""Bluesky client.

Simulates social media activity data.
"""

import os
import pandas as pd
import numpy as np
from datetime import date, timedelta
from pathlib import Path

TARGET_COUNTRIES = ["IRN", "ISR", "USA"]

def generate_synthetic_bluesky(start_date: date, end_date: date, output_dir: Path):
    print(f"Generando datos Bluesky sintéticos desde {start_date} hasta {end_date}...")
    
    dates = []
    d = start_date
    while d <= end_date:
        dates.append(d)
        d += timedelta(days=1)
        
    records = []
    
    for current_date in dates:
        for country in TARGET_COUNTRIES:
            posts = max(0, int(np.random.normal(500, 200)))
            engagement = max(0, np.random.normal(2.5, 1.0))
                
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "country": country,
                "n_social_posts": posts,
                "avg_social_engagement": round(engagement, 2)
            })
            
    df = pd.DataFrame(records)
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = output_dir / "bluesky_aggregated.parquet"
    df.to_parquet(output_path, index=False)
    print(f"✓ Guardado en {output_path} ({len(df)} registros)")
    return df

if __name__ == "__main__":
    np.random.seed(46)
    output_dir = Path("data/raw/bluesky")
    start = date(2024, 1, 1)
    end = date(2026, 5, 8)
    generate_synthetic_bluesky(start, end, output_dir)
