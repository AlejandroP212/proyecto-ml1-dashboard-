"""Integration script for Phase 4.

Combines all normalized sources into a single dataset.
"""

import os
import pandas as pd
from pathlib import Path

def integrate_data():
    proc_dir = Path("data/processed")
    final_dir = Path("data/final")
    
    # Read normalized data
    gdelt_path = proc_dir / "gdelt/normalized.parquet"
    ucdp_path = proc_dir / "ucdp/normalized.parquet"
    rss_path = proc_dir / "rss/normalized.parquet"
    firms_path = proc_dir / "firms/normalized.parquet"
    bluesky_path = proc_dir / "bluesky/normalized.parquet"
    
    if not gdelt_path.exists():
        print("No se encuentra GDELT, abortando integración.")
        return
        
    df = pd.read_parquet(gdelt_path)
    
    if ucdp_path.exists():
        df_ucdp = pd.read_parquet(ucdp_path)
        df = pd.merge(df, df_ucdp, on=["date", "country"], how="left")
        df['n_ucdp_events'] = df['n_ucdp_events'].fillna(0)
        df['total_fatalities'] = df['total_fatalities'].fillna(0)
        
    if rss_path.exists():
        df_rss = pd.read_parquet(rss_path)
        df = pd.merge(df, df_rss, on=["date", "country"], how="left")
        df['n_news_articles'] = df['n_news_articles'].fillna(0)
        
    if firms_path.exists():
        df_firms = pd.read_parquet(firms_path)
        df = pd.merge(df, df_firms, on=["date", "country"], how="left")
        df['n_hotspots'] = df['n_hotspots'].fillna(0)
        df['avg_frp'] = df['avg_frp'].fillna(0.0)
        
    if bluesky_path.exists():
        df_bluesky = pd.read_parquet(bluesky_path)
        df = pd.merge(df, df_bluesky, on=["date", "country"], how="left")
        df['n_social_posts'] = df['n_social_posts'].fillna(0)
        df['avg_social_engagement'] = df['avg_social_engagement'].fillna(0.0)
        
    os.makedirs(final_dir, exist_ok=True)
    df.to_parquet(final_dir / "dataset.parquet", index=False)
    print(f"Integración completa: {len(df)} registros. Guardado en data/final/dataset.parquet")

if __name__ == "__main__":
    integrate_data()
