"""Feature engineering and target creation.

Builds the daily_features dataset and computes the escalation_level target
using UCDP conflict events and fatalities as the primary signal,
complemented by GDELT event volume.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

def build_features_and_target():
    final_dir = Path("data/final")
    input_path = final_dir / "dataset.parquet"
    
    if not input_path.exists():
        print(f"Error: No se encuentra el dataset integrado en {input_path}")
        return
        
    df = pd.read_parquet(input_path)
    
    df = df.sort_values(by=["country", "date"])
    
    df['conflict_events_rolling_3d'] = df.groupby('country')['n_conflict_events'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    df['fatalities_rolling_3d'] = df.groupby('country')['total_fatalities'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    # Target: escalation_level based on UCDP events + fatalities + GDELT event volume
    # This avoids data leakage since avg_goldstein is NOT used for target construction
    # but IS kept as a feature (Goldstein tone is an independent NLP signal from GDELT).
    #
    # Composite conflict score:
    #   score = 0.4 * normalized(n_ucdp_events)
    #         + 0.3 * normalized(total_fatalities)
    #         + 0.3 * normalized(n_conflict_events)
    
    score_cols = ['n_ucdp_events', 'total_fatalities', 'n_conflict_events']
    weights = [0.4, 0.3, 0.3]
    
    composite_score = np.zeros(len(df))
    for col, w in zip(score_cols, weights):
        col_max = df[col].max()
        if col_max > 0:
            normalized = df[col] / col_max
        else:
            normalized = pd.Series(0, index=df.index)
        composite_score += w * normalized.values
    
    df['conflict_score'] = composite_score
    
    for country in df['country'].unique():
        mask = df['country'] == country
        q33 = df.loc[mask, 'conflict_score'].quantile(0.33)
        q66 = df.loc[mask, 'conflict_score'].quantile(0.66)
        
        conditions = [
            df.loc[mask, 'conflict_score'] <= q33,
            (df.loc[mask, 'conflict_score'] > q33) & (df.loc[mask, 'conflict_score'] <= q66),
            df.loc[mask, 'conflict_score'] > q66
        ]
        choices = [0, 1, 2]
        
        df.loc[mask, 'escalation_level'] = np.select(conditions, choices, default=1)
        
    df['escalation_level'] = df['escalation_level'].astype(int)
    
    output_path = final_dir / "features.parquet"
    df.to_parquet(output_path, index=False)
    
    print(f"Features y target construidos. Guardado en {output_path}")
    print("\nDistribución del target por país:")
    print(pd.crosstab(df['country'], df['escalation_level'], margins=True))

if __name__ == "__main__":
    build_features_and_target()
