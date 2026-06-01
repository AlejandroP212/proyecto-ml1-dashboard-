# Definición analítica del proyecto

Este documento describe la formulación del problema de machine learning, la
unidad de análisis, la construcción del target y las decisiones metodológicas
del proyecto.

## Pregunta de trabajo

¿Podemos clasificar el nivel de escalada de una ventana región-día combinando
eventos estructurados, cobertura noticiosa y señales contextuales abiertas sobre
el conflicto Irán-Israel-EE. UU.?

## Versión operativa

Dada una región y una fecha, el sistema estima si esa ventana presenta un nivel
de escalada `bajo`, `medio` o `alto`, usando variables derivadas de:

- eventos estructurados de conflicto (UCDP);
- volumen y tono de noticias (GDELT, RSS);
- señales complementarias de contexto (NASA FIRMS) y señal social (Bluesky).

La salida no es una predicción militar ni una alerta en tiempo real. Es una
clasificación analítica construida con fuentes abiertas, útil para explorar
patrones y límites de los datos OSINT.

## Unidad de análisis

La unidad de análisis es **país-día**. Cada fila del dataset final representa una
región observada durante un día.

Esta unidad se eligió porque:

- permite integrar fuentes con granularidades distintas;
- reduce ruido frente a registros individuales de noticias o eventos;
- facilita construir agregados interpretables;
- permite usar modelos de clasificación vistos en ML1;
- puede representarse de forma clara en un dashboard con filtros de fecha y región.

## Regiones de estudio

| Región | Justificación |
| --- | --- |
| Irán (IRN) | Actor central del conflicto y posible origen o destino de eventos. |
| Israel (ISR) | Actor central y zona de alta cobertura noticiosa y de conflicto. |
| EE.UU. (USA) | Actor relevante como aliado y participante indirecto. |

El período de estudio es `2024-01-01` a `2026-05-08`.

## Tarea de machine learning

**Clasificación supervisada multiclase** del nivel de escalada.

La variable objetivo es `escalation_level`, con tres clases:

| Clase | Etiqueta | Interpretación |
| --- | --- | --- |
| 0 | Bajo | Ventana con pocas señales relevantes, actividad cercana al comportamiento base, ausencia de incidentes fuertes. |
| 1 | Medio | Ventana con señales moderadas: aumento de eventos, mayor volumen noticioso o cambios visibles frente al comportamiento reciente. |
| 2 | Alto | Ventana con concentración fuerte de señales: varios eventos, mayor severidad, alta cobertura mediática o anomalías contextuales coincidentes. |

### Lo que no significa el nivel de escalada

El target no debe interpretarse como:

- probabilidad real de guerra;
- alerta militar;
- confirmación causal de un ataque;
- medición completa de violencia regional;
- evaluación geopolítica definitiva.

Es una variable de trabajo para comparar ventanas país-día y evaluar si las
fuentes abiertas permiten construir una señal analítica razonable.

## Construcción del target

El target se construye mediante un **score compuesto** a partir de variables
factuales, evitando data leakage con las features del modelo.

Componentes del score:

| Variable | Peso | Fuente |
| --- | --- | --- |
| `n_ucdp_events` | 0.4 | UCDP (eventos de violencia organizada) |
| `total_fatalities` | 0.3 | UCDP (fatalidades verificadas) |
| `n_conflict_events` | 0.3 | GDELT (eventos derivados de noticias) |

Procedimiento:

1. Cada componente se normaliza dividiendo por su máximo global.
2. Se calcula `conflict_score = 0.4 × norm(ucdp) + 0.3 × norm(fatalities) + 0.3 × norm(events)`.
3. Por cada país, se calculan los cuantiles 33 y 66 del score.
4. Se asignan clases:
   - `0 (Bajo)`: score ≤ Q33 del país
   - `1 (Medio)`: Q33 < score ≤ Q66
   - `2 (Alto)`: score > Q66

`avg_goldstein` (tono GDELT) se usa como **feature** del modelo pero **no** como
componente del target, para evitar fuga de información.

## Features

### Eventos estructurados (UCDP)

- `n_ucdp_events`: conteo de eventos de violencia organizada por país-día.
- `total_fatalities`: suma de fatalidades verificadas.

### Eventos noticiosos y tono (GDELT)

- `n_conflict_events`: eventos geopolíticos derivados de noticias.
- `avg_goldstein`: escala Goldstein promedio (negativo = conflicto).
- `n_mentions`: menciones mediáticas.
- `has_high_violence`: indicador de eventos de alta violencia.

### Contexto satelital (NASA FIRMS)

- `n_hotspots`: hotspots de fuego detectados por satélite.
- `avg_frp`: potencia radiativa de fuego promedio.

### Cobertura mediática (RSS)

- `n_news_articles`: artículos de noticias del día.

### Señal social (Bluesky)

- `n_social_posts`: posts relacionados con el conflicto.
- `avg_social_engagement`: engagement promedio por post.

### Features derivadas

- `conflict_events_rolling_3d`: media móvil de 3 días de eventos de conflicto.
- `fatalities_rolling_3d`: media móvil de 3 días de fatalidades.

## Modelos

Se compararon 4 modelos de clasificación con validación cruzada temporal:

- **KNN** (k=7, weights='distance')
- **Logistic Regression** (max_iter=1000, class_weight='balanced')
- **Naive Bayes** (GaussianNB)
- **Ridge Classifier** (class_weight='balanced')

Todos los modelos se envuelven en un `Pipeline` con `StandardScaler` y se
evalúan con `TimeSeriesSplit` (5 splits) para respetar el orden temporal.

## Métricas

- **F1-score ponderado** como métrica principal.
- **Precisión y recall ponderados** como métricas complementarias.
- **Matriz de confusión** sobre conjunto de test (20% holdout cronológico).
- **Análisis de errores** desagregado por país y clase.

## Supuestos y decisiones

- Las fuentes abiertas tienen cobertura desigual por país, idioma y tipo de
  evento.
- El volumen de noticias no equivale automáticamente a escalada real.
- El target es una construcción analítica, no una verdad absoluta.
- La unidad país-día puede ocultar eventos intra-día, pero mejora la integración
  multifuente.
- El modelo debe ser explicable para que el dashboard no sea una caja negra.
