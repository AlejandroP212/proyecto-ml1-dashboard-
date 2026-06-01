# Sistema de Inteligencia Multifuente — Conflicto Irán-Israel-EE.UU.

**Proyecto Final · Machine Learning 1**  
**Universidad Externado de Colombia · 2026-I**

**Equipo**: Juan Tomás Rincón Pinzón · Hudy Nicolás Barrera Castañeda · Alejandro Pardo Costo

---

## Descripción

Este proyecto implementa un sistema de inteligencia multifuente que clasifica el
nivel de escalada regional del conflicto Irán-Israel-EE.UU. utilizando
exclusivamente fuentes abiertas y gratuitas (OSINT).

La pregunta de trabajo es:

> ¿Hasta qué punto un conjunto de fuentes abiertas y gratuitas permite detectar,
> clasificar o modelar episodios de escalada regional en el conflicto
> Irán-Israel-EE. UU.?

El sistema combina 5 fuentes de datos heterogéneas, construye un dataset
integrado a nivel país-día, entrena y compara 4 modelos de clasificación
supervisada, y presenta los resultados en un dashboard web interactivo.

## Formulación del problema

**Tarea de ML**: Clasificación supervisada multiclase del nivel de escalada.

**Unidad de análisis**: País-día. Cada fila del dataset representa una región
(Irán, Israel o EE.UU.) en una fecha específica del período 2024-01-01 a
2026-05-08.

**Variable objetivo**: `escalation_level` con tres clases:

| Clase | Etiqueta | Interpretación |
| --- | --- | --- |
| 0 | Bajo | Actividad cercana al comportamiento base de la región. |
| 1 | Medio | Aumento moderado de eventos, cobertura o señales contextuales. |
| 2 | Alto | Concentración fuerte de señales, eventos relevantes o anomalías coincidentes. |

El target se construye mediante un score compuesto a partir de variables
factuales (ver sección [Construcción del target](#construcción-del-target)).

## Fuentes de datos

El proyecto integra 5 fuentes OSINT que cubren los requisitos de diversidad
textual, estructurada, contextual y social:

| Fuente | Tipo | Rol en el proyecto |
| --- | --- | --- |
| **GDELT 2.0** | Textual / eventos noticiosos | Eventos geopolíticos derivados de noticias, tono Goldstein, menciones mediáticas y volumen informativo. |
| **UCDP GED + Candidate** | Estructurada | Eventos georreferenciados de violencia organizada con fatalidades verificadas. Componente factual principal. |
| **NASA FIRMS** | Contexto satelital | Hotspots de fuego detectados por satélite VIIRS como proxy de actividad anómala. |
| **BBC / Al Jazeera RSS** | Textual noticioso | Cobertura mediática complementaria y contraste editorial regional. |
| **Bluesky** | Señal social | Posts y engagement de la red social descentralizada como pulso de conversación pública. |

ACLED fue evaluada pero descartada por depender de credenciales de acceso, lo
que compromete la reproducibilidad del proyecto.

## Construcción del target

El `escalation_level` se construye con un score compuesto que combina señales
factuales independientes, evitando data leakage con las features del modelo:

```
conflict_score = 0.4 × norm(n_ucdp_events) + 0.3 × norm(total_fatalities) + 0.3 × norm(n_conflict_events)
```

Los umbrales de clasificación se definen por cuantiles (Q33, Q66) calculados
dentro de cada país para normalizar las diferencias de línea base regional.

`avg_goldstein` (tono GDELT) se usa como feature del modelo pero no como
componente del target, garantizando que el modelo no pueda "aprender" el target
directamente desde una sola variable.

## Pipeline de datos

El pipeline sigue un flujo reproducible de 4 etapas:

```
Ingesta (src/ingestion/)
  → 5 fuentes → data/raw/

Normalización e integración (src/processing/)
  → data/processed/ → data/final/dataset.parquet

Feature engineering (src/features/)
  → rolling features + target → data/final/features.parquet

Modelado (src/modeling/)
  → TimeSeriesSplit CV → models/ + reports/
```

### Diccionario de features

| Feature | Fuente | Descripción |
| --- | --- | --- |
| `n_conflict_events` | GDELT | Eventos geopolíticos del día |
| `avg_goldstein` | GDELT | Escala Goldstein promedio (negativo = conflicto) |
| `n_mentions` | GDELT | Menciones mediáticas |
| `n_ucdp_events` | UCDP | Eventos de violencia organizada |
| `total_fatalities` | UCDP | Fatalidades verificadas |
| `n_hotspots` | FIRMS | Hotspots de fuego satelital |
| `avg_frp` | FIRMS | Potencia radiativa de fuego promedio |
| `n_news_articles` | RSS | Artículos de noticias del día |
| `n_social_posts` | Bluesky | Posts relacionados con el conflicto |
| `avg_social_engagement` | Bluesky | Engagement promedio por post |
| `conflict_events_rolling_3d` | Derivada | Media móvil de 3 días de eventos |
| `fatalities_rolling_3d` | Derivada | Media móvil de 3 días de fatalidades |

## Modelado

Se entrenaron 4 modelos de clasificación con validación cruzada temporal
(`TimeSeriesSplit`, 5 splits) para respetar el orden cronológico de los datos:

| Modelo | F1 ponderado | Precisión | Recall |
| --- | --- | --- | --- |
| **Logistic Regression** | **0.781 ± 0.028** | **0.777** | **0.771** |
| Ridge Classifier | 0.716 ± 0.023 | 0.733 | 0.706 |
| Naive Bayes | 0.687 ± 0.014 | 0.574 | 0.394 |
| KNN | 0.665 ± 0.046 | 0.782 | 0.776 |

**Mejor modelo**: Logistic Regression con F1 = 0.78.

La partición final usa 80% de los datos para entrenamiento y 20% para test
(respetando orden temporal). El classification report se genera sobre el
conjunto de test, no sobre los datos de entrenamiento.

### Métricas

- **F1-score ponderado** como métrica principal (adecuada para multiclase con
  clases moderadamente balanceadas).
- **Precisión y recall ponderados** como métricas complementarias.
- **Matriz de confusión** sobre test set.
- **Análisis de errores** desagregado por país y clase (`reports/error_analysis.csv`).

## Dashboard

El dashboard web está construido con **Next.js 16** y **Recharts**, e incluye:

- KPIs interactivos de eventos, fatalidades y escalada.
- Filtros por país y rango de fechas que actualizan todas las visualizaciones.
- 5 tipos de gráficos: evolución temporal, distribución por país, eventos por
  mes, radar de fuentes y scatter de eventos vs fatalidades.
- Evaluación comparativa de los 4 modelos con métricas detalladas.
- Descripción de las 5 fuentes OSINT utilizadas.
- Sección de limitaciones y consideraciones éticas.

## Estructura del repositorio

```
.
├── .env.example             # Plantilla de variables de entorno
├── .gitignore
├── data/
│   ├── raw/                 # Datos crudos por fuente
│   ├── processed/           # Datos limpios por fuente
│   └── final/               # Dataset integrado y features
├── docs/                    # Documentación técnica
│   ├── problem_definition.md
│   ├── source_validation.md
│   └── conventions.md
├── notebooks/               # Análisis exploratorio (EDA)
├── src/
│   ├── ingestion/           # Scripts de ingesta y validación por fuente
│   ├── processing/          # Normalización, integración y exportación
│   ├── features/            # Feature engineering y construcción del target
│   └── modeling/            # Entrenamiento y evaluación de modelos
├── models/                  # Modelos serializados
├── dashboard/               # Aplicación web Next.js
├── reports/                 # Resultados, métricas y análisis de errores
├── requirements.txt         # Dependencias Python
└── README.md
```

## Instalación y ejecución

### Pipeline de datos

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ejecutar el pipeline completo desde la raíz del repositorio:

```bash
python src/ingestion/gdelt_client.py
python src/ingestion/ucdp_client.py
python src/ingestion/rss_client.py
python src/ingestion/firms_client.py
python src/ingestion/bluesky_client.py
python src/processing/normalize.py
python src/processing/integrate.py
python src/features/build_features.py
python src/modeling/train.py
python src/processing/export_dashboard.py
```

### Dashboard

```bash
cd dashboard
npm install
npm run build
npm start
```

El dashboard estará disponible en `http://localhost:3000`.

## Limitaciones y consideraciones éticas

- **Sesgo de cobertura mediática**: GDELT deriva eventos de noticias, lo que
  refleja sesgos editoriales, de idioma y de acceso a medios. Eventos en zonas
  remotas o poco cubiertas pueden estar subrepresentados.

- **Niebla de guerra**: En conflictos activos, la información disponible es
  incompleta, contradictoria o potencialmente manipulada. Las fuentes OSINT no
  pueden verificar hechos en terreno.

- **Datos sintéticos**: Esta implementación utiliza datos generados
  sintéticamente para demostración. Las APIs reales fueron validadas
  (`src/ingestion/validate_*.py`) pero el pipeline de producción usa generadores
  con patrones estadísticos realistas basados en las distribuciones observadas.

- **Causalidad vs correlación**: El modelo identifica patrones estadísticos, no
  relaciones causales. Las predicciones no deben usarse para toma de decisiones
  críticas sin validación de expertos en el dominio.

- **UCDP GED 25.1**: La versión anual del dataset tiene cobertura hasta 2024.
  Para 2025-2026 se complementa con UCDP Candidate, que tiene metodología
  ligeramente diferente y debe documentarse como limitación.

## Documentación adicional

- `docs/problem_definition.md` — Definición analítica del problema, unidad de
  análisis, target y métricas.
- `docs/source_validation.md` — Validación detallada de cada fuente, criterios
  de selección y hallazgos.
- `docs/conventions.md` — Convenciones de nombres, estructura de datos y flujo
  de trabajo.
