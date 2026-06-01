"""Model training and evaluation.

Trains 4 models on the daily_features dataset and evaluates them using
TimeSeriesSplit (5 splits) to respect temporal ordering.
Saves the best model and metrics from cross-validation.
"""

import os
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def train_and_evaluate():
    features_path = Path("data/final/features.parquet")
    models_dir = Path("models")
    reports_dir = Path("reports")
    
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(reports_dir / "figures", exist_ok=True)
    
    if not features_path.exists():
        print(f"Error: No se encuentra {features_path}")
        return
        
    df = pd.read_parquet(features_path)
    df = df.sort_values(by=["date", "country"]).reset_index(drop=True)
    
    feature_cols = [
        'n_conflict_events', 'avg_goldstein', 'n_mentions',
        'n_ucdp_events', 'total_fatalities', 'n_hotspots', 'avg_frp',
        'n_news_articles', 'n_social_posts', 'avg_social_engagement',
        'conflict_events_rolling_3d', 'fatalities_rolling_3d'
    ]
    
    existing_cols = [c for c in feature_cols if c in df.columns]
    X = df[existing_cols].fillna(0)
    y = df['escalation_level']
    
    models = {
        'KNN': KNeighborsClassifier(n_neighbors=7, weights='distance'),
        'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced'),
        'Naive Bayes': GaussianNB(),
        'Ridge': RidgeClassifier(class_weight='balanced')
    }
    
    cv_results = {}
    best_f1 = 0
    best_model_name = ""
    best_model = None
    
    tscv = TimeSeriesSplit(n_splits=5)
    
    print("Evaluando modelos con TimeSeriesSplit (5 splits)...")
    
    for name, model in models.items():
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', model)
        ])
        
        scores = cross_validate(
            pipeline, X, y, cv=tscv,
            scoring=['f1_weighted', 'precision_weighted', 'recall_weighted']
        )
        
        f1_mean = scores['test_f1_weighted'].mean()
        f1_std = scores['test_f1_weighted'].std()
        
        cv_results[name] = {
            'f1_weighted_mean': float(f1_mean),
            'f1_weighted_std': float(f1_std),
            'precision_mean': float(scores['test_precision_weighted'].mean()),
            'recall_mean': float(scores['test_recall_weighted'].mean())
        }
        
        print(f"  {name:25s}: F1 = {f1_mean:.4f} +/- {f1_std:.4f}")
        
        if f1_mean > best_f1:
            best_f1 = f1_mean
            best_model_name = name
            best_model = pipeline
            
    print(f"\nMejor modelo: {best_model_name} (F1 = {best_f1:.4f})")
    
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    best_model.fit(X_train, y_train)
    y_pred = best_model.predict(X_test)
    
    joblib.dump(best_model, models_dir / "best_model.joblib")
    
    with open(reports_dir / "cv_results.json", "w") as f:
        json.dump(cv_results, f, indent=4)
    
    with open(reports_dir / "metrics.json", "w") as f:
        json.dump(cv_results, f)
        
    report = classification_report(y_test, y_pred, target_names=["Bajo (0)", "Medio (1)", "Alto (2)"])
    with open(reports_dir / "classification_report.txt", "w") as f:
        f.write(f"Classification Report — {best_model_name} (test set, 20% holdout)\n")
        f.write("=" * 70 + "\n\n")
        f.write(report)
        f.write(f"\n\nCross-validation results (TimeSeriesSplit, 5 splits):\n")
        f.write("-" * 70 + "\n")
        for name, res in cv_results.items():
            f.write(f"  {name:25s}: F1={res['f1_weighted_mean']:.4f} +/- {res['f1_weighted_std']:.4f}\n")
        
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=["Bajo (0)", "Medio (1)", "Alto (2)"],
                yticklabels=["Bajo (0)", "Medio (1)", "Alto (2)"])
    plt.title(f'Matriz de Confusion - {best_model_name} (Test Set)')
    plt.ylabel('Verdadero')
    plt.xlabel('Predicho')
    plt.tight_layout()
    plt.savefig(reports_dir / "confusion_matrix.png")
    plt.close()
    
    errors = df.iloc[split_idx:].copy()
    errors['prediction'] = y_pred
    errors['correct'] = errors['escalation_level'] == errors['prediction']
    
    error_report = errors[~errors['correct']].groupby(['country', 'escalation_level']).size().reset_index(name='count')
    error_report.to_csv(reports_dir / "error_analysis.csv", index=False)
    
    print(f"\nArtefactos guardados en {models_dir} y {reports_dir}")
    print(f"Test set: {len(y_test)} muestras ({split_idx} train / {len(y_test)} test)")

if __name__ == "__main__":
    train_and_evaluate()
