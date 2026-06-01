```
TALLER PRÁCTICO
```
# Proyecto Final ML1: Sistema de

# Inteligencia Multifuente

#### Enunciado oficial · Machine Learning 1 · Ciencia de Datos

```
Julián Zuluaga — Docente
14 de abril de 2026
```

## Enunciado del Proyecto Final

```
Machine Learning 1 (ML1-2026I)
Pregrado en Ciencia de Datos
Universidad Externado de Colombia
```
```
El proyecto parte de un contexto real de escalada regional. La pregunta no es solo qué datos existen, sino
cómo convertirlos en evidencia analítica útil.
```
### Propósito

El proyecto final de Machine Learning 1 busca que cada grupo construya un **sistema
de inteligencia multifuente** alrededor de la escalada del conflicto Irán–Israel–EE.
UU., usando exclusivamente **fuentes gratuitas y públicas**.

La meta no es replicar una plataforma militar o un producto tipo Palantir. La meta es
demostrar criterio de ciencia de datos en cuatro dimensiones:

```
conseguir y documentar datos reales;
construir un dataset integrado y utilizable;
formular y resolver una pregunta propia de machine learning;
comunicar resultados en un dashboard web desplegado.
```
###### 1.

###### 2.

###### 3.

###### 4.


### El reto

Cada grupo de 3 estudiantes deberá proponer, desarrollar y presentar un proyecto
que combine:

```
adquisición de datos por API o web scraping responsable;
análisis exploratorio;
una tarea principal de machine learning alineada con el curso;
un dashboard web desplegado;
una reflexión crítica sobre límites, sesgos y calidad de datos.
```
El proyecto debe ser **propositivo**. Eso significa que el grupo debe tomar decisiones
reales:

```
qué fuentes usar;
cuál será la unidad de análisis;
qué variable objetivo o tarea de ML tendrá sentido;
qué modelos comparar;
cómo traducir el análisis a una interfaz útil.
```
### Pregunta orientadora del curso

```
¿Hasta qué punto un conjunto de fuentes abiertas y gratuitas permite detectar,
clasificar o modelar episodios de escalada regional en el conflicto Irán–Israel–EE.
UU.?
```
Cada grupo puede reformular esta pregunta para convertirla en una versión más
concreta y analíticamente defendible.

### Entregable central

El entregable final es un **sistema de inteligencia multifuente** que incluya:

```
un dataset propio construido por el grupo;
una tarea principal de machine learning;
mínimo 3 modelos comparados;
un dashboard web desplegado;
documentación clara del proceso.
```
###### • • • • • • • • • • • • • • •


### Alcance mínimo obligatorio

Cada grupo debe:

```
trabajar con entre 3 y 5 fuentes;
incluir al menos:
1 fuente textual;
1 fuente estructurada u operativa;
1 fuente adicional de contexto, movilidad o señal social;
formular una pregunta propia;
definir una unidad de análisis;
entrenar mínimo 3 modelos;
comparar resultados con métricas adecuadas;
desplegar un dashboard accesible por URL.
```
### Lo que sí y lo que no es este proyecto

##### Sí es

```
un proyecto de ciencia de datos aplicada;
un problema de ML formulado con datos reales;
una integración entre datos, método y comunicación;
una oportunidad para tomar decisiones propias.
```
##### No es

```
un collage de visualizaciones sin pregunta analítica;
un simple scraping sin modelado;
una copia de un dashboard existente;
una plataforma “militar” o “forense” de tiempo real;
una entrega donde el dashboard sea más importante que el modelo.
```
### Fuentes sugeridas

Las siguientes fuentes son una referencia de partida. No son la única opción, pero sí
representan un conjunto realista y gratuito para trabajar en el curso.

###### • • ◦ ◦ ◦ • • • • • • • • • • • • • •


```
Un proyecto fuerte no necesita decenas de APIs. Necesita combinar bien eventos, noticias, movilidad,
social y contexto.
```
##### Eventos y conflicto estructurado

```
ACLED
UKMTO o fuentes similares de incidentes marítimos
```
##### Noticias y medios

```
GDELT
BBC RSS
Al Jazeera RSS
Google News RSS
```
##### Movilidad

```
OpenSky
AISStream o fuentes equivalentes gratuitas si el grupo logra integrarlas
```
##### Contexto y señales complementarias

```
NASA FIRMS
Cloudflare Radar si el grupo logra autenticarse y consumirla correctamente
otras fuentes abiertas justificadas por el equipo
```
###### • • • • • • • • • • •


##### Social / conversación digital

```
Bluesky
YouTube metadata o comentarios
```
```
Importante: si un grupo quiere usar una fuente adicional, puede hacerlo,
siempre que sea gratuita, pública y documentada en la entrega.
```
### Tabla de fuentes sugeridas

La siguiente tabla resume mejor qué aporta cada fuente y cómo podría entrar al
proyecto.

```
Fuente Tipo deacceso Tipo de datos Qué puede aportar alproyecto
```
```
ACLED API /
registro
```
```
eventos estructurados
de conflicto
```
```
actores, tipo de evento,
fecha, lugar, severidad
aproximada
UKMTO web /
scraping
```
```
incidentes marítimos y
alertas
```
```
riesgo marítimo, seguridad
en Hormuz, contexto
operacional
GDELT API noticias, tono,
menciones
geográficas
```
```
narrativa mediática,
intensidad informativa, NLP
```
```
BBC RSS RSS titulares y enlaces seguimiento editorial y
corpus noticioso
Al Jazeera
RSS
```
```
RSS titulares y enlaces cobertura regional y
contraste editorial
Google News
RSS
```
```
RSS agregación de noticias diversidad de medios y
monitoreoreo temático
OpenSky API estados y trayectorias
de vuelos
```
```
movilidad aérea, densidad,
patrones por ventana
temporal
AISStream tráfico AIS de buques
```
###### •

###### •


```
Fuente Tipo deacceso Tipo de datos Qué puede aportar alproyecto
WebSocket
API
```
```
movilidad marítima,
actividad en rutas críticas
NASA FIRMS API hotspots e incendios
satelitales
```
```
contexto geoespacial,
señales térmicas, actividad
anómala
Cloudflare
Radar
```
```
API conectividad y
anomalías de internet
```
```
contexto digital, caídas,
actividad de red
Bluesky API posts y conversación
pública
```
```
capa social, texto corto,
señales discursivas
YouTube API /
metadata
```
```
videos, títulos,
descripciones,
comentarios
```
```
conversación audiovisual,
contexto explicativo,
comentarios
```
##### Cómo pensar estas fuentes

```
Eventos: ayudan a construir labels o targets.
Noticias: ayudan a construir corpus textual, narrativa y embeddings.
Movilidad: ayudan a capturar comportamiento operativo por tiempo y región.
Social: ayudan a observar discurso público o conversación digital.
Contexto: ayudan a enriquecer explicaciones o crear features adicionales.
```
###### •

###### •

###### •

###### •

###### •


### Sugerencias para conseguir datos

```
El proyecto no se evalúa por descargar APIs, sino por transformar fuentes heterogéneas en un pipeline
claro y reproducible.
```
##### 1. No empiecen por el dashboard

Empiecen por definir:

```
qué quieren explicar o predecir;
qué unidad de análisis van a usar;
qué datos podrían respaldar esa pregunta.
```
##### 2. Bajen primero una muestra pequeña

Antes de “montar todo”, prueben:

```
si la fuente responde;
qué campos trae;
qué tan limpia está;
qué tanto ruido tiene;
si realmente sirve para su pregunta.
```
##### 3. Normalicen desde el principio

Intenten que toda fuente termine, al menos, con campos comparables como:

```
timestamp
```
###### • • • • • • • • •


```
source
country
lat
lon
text
event_type
value o score
```
##### 4. Documenten sus decisiones

Cada grupo debe poder responder:

```
por qué eligió esas fuentes;
qué dejó por fuera;
qué limpió;
qué supuestos hizo;
qué limitaciones encontró.
```
##### 5. No persigan “tiempo real” perfecto

No es necesario tener streaming completo o una infraestructura profesional. Es
preferible:

```
un pipeline pequeño pero reproducible,
```
que

```
una promesa ambiciosa que no se puede sostener técnicamente.
```
### Unidad de análisis: decisión crítica

El grupo debe escoger y justificar su unidad de análisis.

Opciones razonables:

```
documento: noticia, post o comentario;
evento: incidente, alerta o registro individual;
ventana temporal: país-día, región-6h, región-12h.
```
La unidad de análisis condiciona:

```
el target;
los features;
```
###### • • • • • • • • • • • • • • • • • • •


```
los modelos;
las métricas;
el diseño del dashboard.
```
### Problemas de ML posibles

El grupo debe definir una tarea principal de machine learning. Estas son referencias
posibles, no una lista cerrada.

##### 1. Clasificación supervisada

Ejemplos:

```
clasificar noticias o posts por tipo de narrativa;
clasificar ventanas temporales por nivel de escalada;
clasificar regiones o periodos por riesgo operativo.
```
##### 2. Regresión

Ejemplos:

```
estimar intensidad mediática;
predecir número de eventos en la siguiente ventana;
construir un score continuo de riesgo.
```
##### 3. Clustering como apoyo

Ejemplos:

```
agrupar narrativas;
identificar perfiles de días o regiones;
explorar similitud semántica en noticias o posts.
```
```
Nota: el clustering no reemplaza la tarea principal. Puede ser una capa
exploratoria adicional.
```
### Alineación con los temas reales del curso

De acuerdo con la estructura actual de ML1-2026I registrada en Academy, los temas
del curso incluyen:

```
fundamentos del aprendizaje supervisado
```
###### • • • • • • • • • • • • •


```
KNN
Naive Bayes
K-Means
métricas de evaluación
balanceo de clases
validación
feature engineering y pipelines
regresión lineal
clasificación lineal
regularización
despliegue
diagnóstico y ética
```
Esto significa que el proyecto final debe estar **anclado primero a los modelos y
conceptos vistos en clase**.

### Modelos compatibles con el curso

Dependiendo del problema planteado, pueden considerarse:

```
KNN
Naive Bayes
K-Means
Linear Regression
Logistic Regression
modelos lineales con regularización como Ridge y Lasso
```
##### Modelos adicionales permitidos

Si un grupo quiere usar modelos adicionales, puede hacerlo, siempre que:

```
mantenga una línea base basada en modelos del curso;
justifique por qué el modelo adicional aporta valor;
siga siendo capaz de explicar con claridad el procedimiento y la evaluación.
```
Ejemplos de modelos adicionales aceptables:

```
Decision Tree
Random Forest
```
###### • • • • • • • • • • • • • • • • • • • • • • •


```
Gradient Boosting
```
La regla no es “usar lo más complejo posible”, sino demostrar criterio y comparación.

##### Sobre embeddings

Se permite el uso de embeddings para representar texto, agrupar documentos o
enriquecer features, siempre que:

```
tengan una justificación clara;
se comparen con una línea base simple;
no sustituyan la explicación del problema.
```
Ejemplos válidos:

```
TF-IDF + Logistic Regression vs Embeddings + Logistic Regression
TF-IDF + Naive Bayes vs Embeddings + KNN
```
### Qué debe mostrar el dashboard

```
El dashboard debe ser ambicioso y atractivo, pero siempre conectado con fuentes, métricas, modelos y
hallazgos reales.
```
El dashboard final debe incluir, como mínimo:

```
una explicación breve del problema del grupo;
las fuentes usadas;
```
###### • • • • • • • •


```
visualizaciones exploratorias;
filtros por fecha, región, categoría o fuente;
resultados del modelo;
métricas principales;
interpretación de hallazgos;
limitaciones del sistema.
```
El dashboard debe estar **desplegado en web** y debe ser navegable por una persona
externa al grupo.

##### Herramientas posibles

Se permiten, entre otras:

```
Streamlit
Dash
Shiny for Python
Next.js
Plotly, Leaflet, Folium, MapLibre o herramientas equivalentes
```
No se exige una tecnología específica. Se evalúa la calidad del producto final, no el
framework.

### Estructura sugerida del proyecto

Una estructura razonable del repositorio podría incluir:

```
data/
notebooks/ o src/
scripts/
models/
dashboard/
README.md
requirements.txt o pyproject.toml
```
###### • • • • • • • • • • • • • • • • • •


### Entregables

Cada grupo deberá entregar:

```
Repositorio del proyecto
código limpio y ejecutable;
instrucciones de instalación;
documentación clara.
Dataset o pipeline de construcción del dataset
no es necesario subir archivos masivos si hay restricción de tamaño;
sí es obligatorio explicar cómo se construye.
Análisis exploratorio
visualizaciones;
hallazgos;
problemas de calidad de datos.
Modelado
problema definido;
features;
modelos comparados;
métricas;
análisis de errores.
Dashboard web desplegado
URL accesible;
navegación clara;
integración entre datos, análisis y modelo.
Presentación final
síntesis de problema, método, resultados y aprendizajes.
```
### Criterios de evaluación

##### 1. Formulación del problema

```
¿La pregunta es clara?
```
###### 1.

###### ◦

###### ◦

###### ◦

###### 2.

###### ◦

###### ◦

###### 3.

###### ◦

###### ◦

###### ◦

###### 4.

###### ◦

###### ◦

###### ◦

###### ◦

###### ◦

###### 5.

###### ◦

###### ◦

###### ◦

###### 6.

###### ◦

###### •


```
¿La tarea de ML tiene sentido?
¿La unidad de análisis está bien definida?
```
##### 2. Calidad del dataset

```
¿Las fuentes están justificadas?
¿El dataset está limpio y documentado?
¿Se reconocen sesgos y limitaciones?
```
##### 3. Modelado y rigor técnico

```
¿Hay una línea base?
¿Se comparan modelos con criterio?
¿Las métricas corresponden al problema?
¿Hay análisis de errores?
```
##### 4. Dashboard y comunicación

```
¿El dashboard aporta valor real?
¿Explica los resultados con claridad?
¿Conecta visualmente fuentes, análisis y modelo?
```
##### 5. Calidad integral del proyecto

```
¿Es reproducible?
¿Está bien documentado?
¿Muestra criterio y autonomía?
```
### Consejos para un proyecto fuerte

```
Es mejor una pregunta pequeña y bien resuelta que un sistema gigantesco y
frágil.
Si una fuente no funciona, documenten el intento y cambien de estrategia.
No se obsesionen con “capturarlo todo”.
Elijan una unidad de análisis estable.
Si usan embeddings, compárenlos con una línea base clásica.
Eviten targets imposibles de justificar.
El dashboard debe mostrar también límites y decisiones, no solo éxitos.
```
###### • • • • • • • • • • • • • • • • • • • • • •


### Errores frecuentes a evitar

```
bajar muchas fuentes sin una pregunta clara;
construir el dashboard antes del dataset;
usar modelos sin entender qué predicen;
confundir visualización con machine learning;
no documentar limpieza y transformaciones;
no explicar de dónde salió el target;
no evaluar errores reales del modelo.
```
### Glosario mínimo

**Unidad de análisis**
La entidad que representa cada fila principal del dataset. Puede ser un documento, un
evento o una ventana temporal.

**Target / variable objetivo**
La variable que el grupo quiere predecir, clasificar o estimar.

**Feature**
Variable de entrada usada por el modelo para aprender patrones.

**Label**
Etiqueta asociada a un ejemplo. En clasificación, normalmente corresponde a la
categoría esperada.

**EDA**
Análisis exploratorio de datos. Sirve para entender distribuciones, relaciones,
problemas de calidad y posibles sesgos.

**Embedding**
Representación numérica densa de texto u objetos, útil para medir similitud o
enriquecer modelos.

**Pipeline**
Secuencia reproducible de pasos para capturar, limpiar, transformar y modelar datos.

**Baseline**
Modelo o aproximación simple que sirve como punto de comparación.

**Validación**
Proceso para estimar qué tan bien generaliza un modelo y evitar conclusiones
engañosas.

###### • • • • • • •


**Balanceo de clases**
Estrategias para tratar datasets donde unas categorías aparecen mucho más que
otras.

**Regularización**
Mecanismo para controlar la complejidad del modelo y reducir sobreajuste.

**Despliegue**
Paso en el que el análisis o el modelo se integra en un producto accesible, en este
caso un dashboard web.

**OSINT**
Open-Source Intelligence. Uso de fuentes abiertas para producir información
estructurada y útil.

### Recomendación metodológica

Una ruta sana para la mayoría de grupos es:

```
escoger una pregunta concreta;
validar 2 o 3 fuentes primero;
construir una tabla integrada;
hacer EDA serio;
definir target y features;
entrenar y comparar modelos;
recién ahí diseñar el dashboard final.
```
### Cierre

Este proyecto no busca que todos lleguen a la misma respuesta. Busca que cada
grupo sea capaz de:

```
formular un problema propio;
conseguir datos abiertos útiles;
construir un dataset defendible;
aplicar con criterio técnicas de Machine Learning 1;
y traducir todo eso en un producto web que comunique con claridad.
```