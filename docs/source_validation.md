# Validación de fuentes

Este documento registra el proceso de evaluación y selección de fuentes de datos
para el proyecto. Cada fuente fue evaluada con los mismos criterios antes de
integrarse al pipeline.

## Criterios de evaluación

| Criterio | Pregunta de control |
| --- | --- |
| Acceso | ¿La fuente es pública, gratuita y accesible desde el entorno de trabajo? |
| Reproducibilidad | ¿Se puede consultar con un script o URL documentada? |
| Cobertura temporal | ¿Cubre el período `2024-01-01` a `2026-05-08` o una parte útil? |
| Cobertura geográfica | ¿Permite filtrar o inferir regiones del proyecto? |
| Campos útiles | ¿Aporta texto, eventos, fecha, región, coordenadas, actores, tono o señales agregables? |
| Calidad | ¿Hay duplicados, ruido, campos faltantes o sesgos claros? |
| Integración | ¿Puede agregarse a la unidad país-día? |
| Riesgo | ¿Tiene límites técnicos, éticos, legales o metodológicos relevantes? |

## Resumen de fuentes

| Fuente | Tipo | Decisión | Justificación |
| --- | --- | --- | --- |
| GDELT 2.0 | Textual / eventos noticiosos | ✅ Seleccionada | Cobertura global, API gratuita, eventos + tono + menciones |
| UCDP GED + Candidate | Estructurada | ✅ Seleccionada | Eventos de violencia con fatalidades verificadas, descarga pública |
| NASA FIRMS | Contexto satelital | ✅ Seleccionada | Hotspots de fuego, API gratuita, señal contextual |
| BBC / Al Jazeera RSS | Textual noticioso | ✅ Seleccionada | Cobertura mediática en tiempo real, contraste editorial |
| Bluesky | Señal social | ✅ Seleccionada | Red social descentralizada, API abierta |
| ACLED | Estructurada | ❌ Descartada | Requiere credenciales, compromete reproducibilidad |
| OpenSky | Movilidad aérea | ❌ Descartada | Cobertura insuficiente para las regiones de estudio |

## Fuente 1: GDELT 2.0

### Rol en el proyecto

GDELT aporta la capa textual y de eventos noticiosos:

- volumen de noticias relacionadas con regiones y actores;
- títulos, URLs, idiomas y países de origen de medios;
- menciones y tono mediante datasets GDELT 2.0;
- eventos derivados de noticias como señal complementaria.

### Documentación

- Página oficial: https://www.gdeltproject.org/data.html
- API DOC 2.0: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- Codebook Event Database V2.0: https://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
- Codebook GKG V2.0: https://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.pdf

### Validación

Script: `src/ingestion/validate_gdelt.py`

Se validaron dos superficies de acceso:

**API DOC 2.0**: acceso exitoso, retorna artículos con campos de idioma, país de
origen y dominio. La API tiene límites de tasa (1 request cada 5 segundos).

**Archivos crudos GDELT 2.0**: archivos de eventos, menciones y GKG disponibles
cada 15 minutos con esquema consistente. Se confirmó cobertura para el período
`2024-01-01` a `2026-05-08`.

En una muestra de 15 minutos se observaron 280 filas con códigos de regiones del
proyecto: Irán (189), Israel (62), Líbano (10), Siria (10), Irak (7), Gaza (2).

### Campos utilizados

- `SQLDATE`, `DATEADDED`: fecha del evento.
- `Actor1Name`, `Actor2Name`: actores del evento.
- `EventCode`, `QuadClass`: tipo de evento.
- `GoldsteinScale`: intensidad (negativo = conflicto).
- `NumMentions`, `NumSources`, `NumArticles`: volumen mediático.
- `ActionGeo_CountryCode`, latitud, longitud: geografía.

### Limitaciones

- GDELT deriva eventos de noticias, no es un registro directo de hechos.
- Puede duplicar eventos cuando múltiples medios reportan lo mismo.
- El volumen mediático puede reflejar interés editorial, no escalada real.
- La API DOC tiene límites de tasa estrictos.

## Fuente 2: UCDP GED + UCDP Candidate

### Rol en el proyecto

UCDP aporta la capa factual estructurada:

- eventos individuales de violencia organizada;
- fecha y georreferenciación al nivel de día y lugar;
- país, coordenadas y variables de severidad (fatalidades);
- componente principal del target de escalada.

### Documentación

- Dataset Download Center: https://ucdp.uu.se/downloads/
- API Documentation: https://ucdp.uu.se/apidocs/index.html

### Validación

Script: `src/ingestion/validate_ucdp.py`

Se validaron dos productos:

**UCDP GED 25.1**: cubre eventos de violencia organizada de 1989 a 2024.
Descarga pública sin credenciales. Licencia CC BY 4.0.

**UCDP Candidate 26.0.4**: releases mensuales con rezago corto para extender
cobertura a 2025-2026.

Reporte completo: `reports/tables/ucdp_validation_summary.md`

### Limitaciones

- GED anual llega a 2024; para 2025-2026 se complementa con Candidate.
- Candidate tiene metodología ligeramente diferente y debe documentarse.
- La integración de dos releases exige cuidado con columnas, IDs y deduplicación.
- Cobertura desigual por país: Israel domina los eventos recientes.

## Fuente 3: NASA FIRMS

### Rol en el proyecto

NASA FIRMS aporta la capa de contexto satelital:

- hotspots de fuego detectados por satélite VIIRS;
- potencia radiativa de fuego (FRP) como proxy de intensidad;
- señal contextual complementaria a eventos y noticias.

### Documentación

- NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/

### Validación

Script: `src/ingestion/validate_firms.py`

La API es gratuita y no requiere autenticación para consultas básicas. Los datos
incluyen coordenadas, fecha, FRP y confianza de detección.

### Limitaciones

- Los hotspots pueden corresponder a incendios forestales, quemas agrícolas u
  otras actividades no relacionadas con el conflicto.
- La cobertura es global pero la relevancia para el conflicto debe filtrarse por
  contexto geográfico y temporal.

## Fuente 4: BBC / Al Jazeera RSS

### Rol en el proyecto

Los feeds RSS aportan la capa de cobertura mediática en tiempo real:

- artículos en inglés con título, descripción, fecha y enlace;
- señal de intensidad mediática que complementa la señal factual de UCDP;
- contraste editorial entre fuentes occidentales y regionales.

### Validación

Script: `src/ingestion/validate_rss.py`

| Feed | Artículos | Relevancia al conflicto |
| --- | --- | --- |
| BBC News – Middle East | 40 | 97.5% (39/40) |
| Al Jazeera English | 25 | 36.0% (9/25) |

BBC Middle East tiene alta relevancia. Al Jazeera English es el feed global con
cobertura mixta; en producción se puede usar el feed específico de Medio Oriente.

Reuters fue evaluado pero falló por DNS no resoluble desde el entorno de trabajo.

Reporte completo: `reports/tables/rss_validation_summary.md`

### Limitaciones

- Los feeds RSS solo proporcionan titulares y descripciones, no texto completo.
- La frecuencia de actualización varía entre fuentes.
- Al Jazeera global tiene baja relevancia relativa para el conflicto específico.

## Fuente 5: Bluesky

### Rol en el proyecto

Bluesky aporta la capa de señal social:

- posts y conversación pública sobre el conflicto;
- engagement (likes, reposts, replies) como proxy de atención social;
- texto corto para análisis de sentimiento o temas.

### Documentación

- API AT Protocol: https://atproto.com/

### Validación

Script: `src/ingestion/validate_bluesky.py`

La API de Bluesky es abierta y no requiere autenticación para consultas públicas.
Se pueden buscar posts por keywords relacionados con el conflicto.

### Limitaciones

- Bluesky tiene una base de usuarios más pequeña que otras redes sociales.
- La representatividad demográfica puede estar sesgada.
- El volumen de posts sobre el conflicto puede ser bajo comparado con otras fuentes.

## Fuente descartada: ACLED

### Evaluación

ACLED fue evaluada como candidata principal para la capa estructurada por su
reconocimiento en investigación de conflictos.

Script: `src/ingestion/validate_acled.py`

### Razón de descarte

ACLED requiere credenciales (email + password o API key) para acceder a su API.
Esto compromete la reproducibilidad del proyecto:

- no es completamente abierto ni gratuito en la práctica;
- agrega fricción para que terceros repliquen el pipeline;
- las credenciales pueden expirar o cambiar.

Se priorizó UCDP como alternativa que ofrece descarga pública sin credenciales.
