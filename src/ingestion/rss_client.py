"""RSS Feeds client.

Simulates the aggregation of news articles from RSS feeds (BBC, Al Jazeera, etc.)
over the historical period.
"""

import os
import pandas as pd
import numpy as np
from datetime import date, timedelta
from pathlib import Path

TARGET_COUNTRIES = ["IRN", "ISR", "USA"]

def generate_synthetic_rss(start_date: date, end_date: date, output_dir: Path):
    print(f"Generando datos RSS sintéticos desde {start_date} hasta {end_date}...")
    
    dates = []
    d = start_date
    while d <= end_date:
        dates.append(d)
        d += timedelta(days=1)
        
    records = []
    
    for current_date in dates:
        for country in TARGET_COUNTRIES:
            if country == "ISR":
                articles = int(np.random.normal(30, 10))
            elif country == "USA":
                articles = int(np.random.normal(40, 15))
            else:
                articles = int(np.random.normal(20, 8))
                
            # Add some correlation with time to simulate news cycles
            noise = np.sin(current_date.toordinal() / 10.0) * 10
            articles = max(0, int(articles + noise))
                
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "country": country,
                "n_news_articles": articles
            })
            
    df = pd.DataFrame(records)
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = output_dir / "rss_aggregated.parquet"
    df.to_parquet(output_path, index=False)
    print(f"✓ Guardado en {output_path} ({len(df)} registros)")
    return df

if __name__ == "__main__":
    np.random.seed(44)
    output_dir = Path("data/raw/rss")
    start = date(2024, 1, 1)
    end = date(2026, 5, 8)
    generate_synthetic_rss(start, end, output_dir)
