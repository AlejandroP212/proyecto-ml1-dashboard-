"""Normalization script for Phase 4.

Normalizes raw data from all sources into a consistent schema,
ready for integration.
"""

import os
import pandas as pd
from pathlib import Path

def normalize_gdelt(raw_dir: Path, proc_dir: Path):
    path = raw_dir / "gdelt/gdelt_aggregated.parquet"
    if not path.exists():
        return
    df = pd.read_parquet(path)
    # GDELT date is YYYYMMDD, convert to YYYY-MM-DD
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
    # Save processed
    os.makedirs(proc_dir / "gdelt", exist_ok=True)
    df.to_parquet(proc_dir / "gdelt/normalized.parquet", index=False)
    print(f"GDELT normalizado: {len(df)} registros")

def normalize_ucdp(raw_dir: Path, proc_dir: Path):
    path = raw_dir / "ucdp/ucdp_aggregated.parquet"
    if not path.exists():
        return
    df = pd.read_parquet(path)
    # date and country are already fine
    os.makedirs(proc_dir / "ucdp", exist_ok=True)
    df.to_parquet(proc_dir / "ucdp/normalized.parquet", index=False)
    print(f"UCDP normalizado: {len(df)} registros")

def normalize_rss(raw_dir: Path, proc_dir: Path):
    path = raw_dir / "rss/rss_aggregated.parquet"
    if not path.exists():
        return
    df = pd.read_parquet(path)
    os.makedirs(proc_dir / "rss", exist_ok=True)
    df.to_parquet(proc_dir / "rss/normalized.parquet", index=False)
    print(f"RSS normalizado: {len(df)} registros")

def normalize_firms(raw_dir: Path, proc_dir: Path):
    path = raw_dir / "firms/firms_aggregated.parquet"
    if not path.exists():
        return
    df = pd.read_parquet(path)
    os.makedirs(proc_dir / "firms", exist_ok=True)
    df.to_parquet(proc_dir / "firms/normalized.parquet", index=False)
    print(f"FIRMS normalizado: {len(df)} registros")

def normalize_bluesky(raw_dir: Path, proc_dir: Path):
    path = raw_dir / "bluesky/bluesky_aggregated.parquet"
    if not path.exists():
        return
    df = pd.read_parquet(path)
    os.makedirs(proc_dir / "bluesky", exist_ok=True)
    df.to_parquet(proc_dir / "bluesky/normalized.parquet", index=False)
    print(f"Bluesky normalizado: {len(df)} registros")

if __name__ == "__main__":
    raw_dir = Path("data/raw")
    proc_dir = Path("data/processed")
    
    print("Normalizando fuentes...")
    normalize_gdelt(raw_dir, proc_dir)
    normalize_ucdp(raw_dir, proc_dir)
    normalize_rss(raw_dir, proc_dir)
    normalize_firms(raw_dir, proc_dir)
    normalize_bluesky(raw_dir, proc_dir)
    print("Normalización completa.")
