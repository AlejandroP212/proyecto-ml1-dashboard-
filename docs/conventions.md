# Convenciones del proyecto

Este documento define las reglas de estructura, nombres y ejecución para
garantizar reproducibilidad.

## Estructura de datos

- `data/raw/`: datos crudos por fuente, sin modificar. No se editan manualmente.
- `data/processed/`: datos limpios y normalizados por fuente.
- `data/final/`: dataset integrado y features para modelado y dashboard.

Los archivos de datos no se suben al repositorio. Cada dataset puede
reconstruirse ejecutando los scripts de ingesta y procesamiento.

## Nombres de archivos

Los scripts de Python usan nombres descriptivos en minúsculas con guiones bajos:

```text
src/ingestion/gdelt_client.py
src/processing/normalize.py
src/features/build_features.py
src/modeling/train.py
```

Los datos intermedios usan nombres descriptivos por etapa:

```text
data/raw/gdelt/                    # datos crudos por fuente
data/processed/gdelt/normalized.parquet
data/final/dataset.parquet         # dataset integrado
data/final/features.parquet        # features + target
```

## Columnas del dataset integrado

El dataset en `data/final/features.parquet` usa las siguientes columnas:

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `date` | date | Fecha de la observación |
| `country` | str | Código de país (IRN, ISR, USA) |
| `n_conflict_events` | int | Eventos GDELT del día |
| `avg_goldstein` | float | Tono Goldstein promedio |
| `n_mentions` | int | Menciones mediáticas |
| `n_ucdp_events` | int | Eventos UCDP |
| `total_fatalities` | int | Fatalidades verificadas |
| `n_hotspots` | int | Hotspots FIRMS |
| `avg_frp` | float | Potencia radiativa promedio |
| `n_news_articles` | int | Artículos RSS |
| `n_social_posts` | int | Posts Bluesky |
| `avg_social_engagement` | float | Engagement promedio |
| `conflict_events_rolling_3d` | float | Media móvil 3 días |
| `fatalities_rolling_3d` | float | Media móvil 3 días |
| `escalation_level` | int | Target: 0=Bajo, 1=Medio, 2=Alto |

## Ejecución

El pipeline se ejecuta desde la raíz del repositorio en este orden:

1. Ingesta: `src/ingestion/*_client.py` (uno por fuente)
2. Normalización: `src/processing/normalize.py`
3. Integración: `src/processing/integrate.py`
4. Features: `src/features/build_features.py`
5. Modelado: `src/modeling/train.py`
6. Export dashboard: `src/processing/export_dashboard.py`

## Dashboard

El dashboard Next.js está en `dashboard/` y se ejecuta de forma independiente:

```bash
cd dashboard
npm install
npm run build
npm start
```
