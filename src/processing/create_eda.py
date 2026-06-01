"""Generates the EDA notebook."""

import os
import nbformat as nbf
from pathlib import Path

def create_eda_notebook():
    nb = nbf.v4.new_notebook()
    
    cells = [
        nbf.v4.new_markdown_cell("# EDA - Proyecto Final ML1\n\nEste notebook contiene el análisis exploratorio de datos de las fuentes integradas."),
        
        nbf.v4.new_code_cell("""import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Configuraciones de visualización\nsns.set_theme(style="whitegrid")\nplt.rcParams['figure.figsize'] = (10, 6)"""),
        
        nbf.v4.new_markdown_cell("## 1. Carga de datos"),
        
        nbf.v4.new_code_cell("""df = pd.read_parquet('../data/final/features.parquet')\ndf['date'] = pd.to_datetime(df['date'])\ndf.head()"""),
        
        nbf.v4.new_markdown_cell("## 2. Distribución del Nivel de Escalada (Target)"),
        
        nbf.v4.new_code_cell("""plt.figure(figsize=(8, 5))\nsns.countplot(data=df, x='escalation_level', hue='country', palette='Set2')\nplt.title('Distribución del Nivel de Escalada por País')\nplt.xlabel('Nivel de Escalada (0=Bajo, 1=Medio, 2=Alto)')\nplt.ylabel('Días')\nplt.show()"""),
        
        nbf.v4.new_markdown_cell("## 3. Serie temporal de Tono Goldstein y Eventos"),
        
        nbf.v4.new_code_cell("""fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)\n\nsns.lineplot(ax=axes[0], data=df, x='date', y='avg_goldstein', hue='country')\naxes[0].set_title('Tono Promedio Goldstein en el Tiempo')\naxes[0].set_ylabel('Goldstein')\n\nsns.lineplot(ax=axes[1], data=df, x='date', y='n_conflict_events', hue='country')\naxes[1].set_title('Eventos de Conflicto en el Tiempo')\naxes[1].set_ylabel('Número de Eventos')\n\nplt.tight_layout()\nplt.show()"""),
        
        nbf.v4.new_markdown_cell("## 4. Correlación de Variables"),
        
        nbf.v4.new_code_cell("""numeric_cols = ['n_conflict_events', 'avg_goldstein', 'n_mentions', \n                'n_ucdp_events', 'total_fatalities', 'n_hotspots', 'avg_frp', \n                'n_news_articles', 'n_social_posts', 'avg_social_engagement']\n\nplt.figure(figsize=(10, 8))\ncorr = df[numeric_cols].corr()\nsns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.2f')\nplt.title('Matriz de Correlación')\nplt.show()""")
    ]
    
    nb['cells'] = cells
    
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/eda.ipynb', 'w') as f:
        nbf.write(nb, f)
        
    print("Notebook EDA generado en notebooks/eda.ipynb")

if __name__ == "__main__":
    create_eda_notebook()
