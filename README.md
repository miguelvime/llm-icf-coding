# Codificación automatizada de historias clínicas a la CIF con LLMs

Codificación de texto clínico no estructurado con la Clasificación Internacional del Funcionamiento (CIF) de la OMS mediante LLMs, usando el consenso estricto de tres iteraciones (3/3). Validado sobre 24 categorías CIF de dolor crónico.

El repositorio tiene dos partes: los flujos de n8n que codifican los textos y los scripts de R que evalúan el resultado.

## 1. Reproducir el estudio

### Con Docker

```bash
cd infrastructure
docker compose run --rm analysis
```

### En local

Requiere R 4.1 o superior.

```bash
Rscript -e 'install.packages(c("jsonlite", "irrCAC", "dplyr", "ggplot2", "scales", "patchwork", "rmarkdown"))'
Rscript analisis/ejecutar_todo.R
```

Los resultados se muestran en la consola y se guardan en `results/resultados.txt`. Las figuras se guardan en `results/figuras/`.

Cada script se puede ejecutar por separado desde la carpeta principal del proyecto, por ejemplo `Rscript analisis/02_f1_score.R`.

| Script | Qué calcula |
|---|---|
| `00_comun.R` | Rutas de los datos, los 24 códigos y las funciones de métricas que usan los demás scripts |
| `01_fiabilidad.R` | Acuerdo exacto, Po, AC1 de Gwet y alfa de Krippendorff entre las 3 iteraciones |
| `02_f1_score.R` | Precisión, sensibilidad y F1 micro, macro y weighted con IC 95 %, y diferencias entre modelos |
| `03_ablacion_b280.R` | Las mismas métricas sin el código dominante b280 |
| `04_humanos.R` | Fiabilidad, F1 y ablación en las historias escritas por fisioterapeutas |
| `05_estrategias_consenso.R` | Cada iteración por separado frente a consenso 3/3, mayoría 2/3 y unión 1/3 |
| `06_figuras.R` | Figuras |
| `07_tablas.R` | Tablas de resultados |

Los IC 95 % se calculan con 2000 remuestras bootstrap por combinación de códigos (`id_code_combination`) y semilla 2026. De las 21 historias de fisioterapeutas se excluyen las 2 que se usaron como ejemplo en el prompt (`002_1` y `012_1`).

## 2. Analizar tus propios datos

### Paso 1: codificar los textos

Prepara un JSON con un identificador y el texto de cada historia:

```json
[
  { "id_clinical_text": "01", "clinical_text": "Paciente de 45 años con dolor lumbar crónico y limitación funcional..." }
]
```

Codifícalo con n8n (sección 3). El archivo resultante incluye los códigos de cada iteración (`predicted_icf_it1`, `predicted_icf_it2`, `predicted_icf_it3`) y los del consenso 3/3 (`predicted_icf_codes_consensus`).

### Paso 2: generar el informe

```bash
Rscript analisis/analizar.R ruta/a/tu_archivo_codificado.json "Mi hospital / Cohorte 2026"
```

Con Docker (la ruta del archivo es relativa a la carpeta principal del proyecto):

```bash
cd infrastructure
docker compose run --rm analysis Rscript analisis/analizar.R ruta/a/tu_archivo_codificado.json "Mi hospital / Cohorte 2026"
```

Se genera `results/informe_<nombre del archivo>.html`, un HTML autónomo que se abre con cualquier navegador:

- Siempre: número de historias, códigos asignados, frecuencia de cada código y acuerdo entre las tres iteraciones (acuerdo exacto, Po, AC1 y alfa).
- Si el archivo incluye una codificación de referencia en `icf_codes`: precisión, sensibilidad y F1 (micro, macro y weighted), exact match ratio, F1 por código y las historias con falsos positivos o falsos negativos.

Para generar el HTML hace falta pandoc, que viene con RStudio y con la imagen de Docker.

## 3. Configurar y ejecutar n8n

1. Levanta el servicio con `cd infrastructure && docker compose up -d n8n` y entra en `http://localhost:5679`.
2. Importa desde `n8n_workflows/` el flujo del modelo que quieras usar:
   - `2026-08-25-gemini-3.7-flash-codifier.json` (Gemini 3.7 Flash)
   - `2026-08-25-gemini-3.5-flash-codifier.json` (Gemini 3.5 Flash)
   - `2026-08-25-gemma-4-31b-it-codifier.json` (Gemma-4-31B-it)
   - `2026-09-03_generic_LLM_codifier.json`, un flujo genérico que puedes adaptar a cualquier modelo.
3. Pulsa **Execute Workflow** y carga el JSON que quieres codificar.

## Verificación en Python (opcional)

`scripts_test/` repite los análisis 01 a 05 en Python con scikit-learn y la versión de irrCAC para Python. Sirve para comprobar que dos implementaciones independientes dan las mismas estimaciones. Los IC bootstrap cambian ligeramente porque el generador de números aleatorios es distinto.

```bash
pip install numpy pandas scikit-learn irrCAC
python scripts_test/02_f1_score.py
```

## Estructura

```
analisis/          Scripts de R: análisis, figuras, tablas e informe
data/              Historias sintéticas (generator_output.json, N = 114) y de fisioterapeutas (physio_created_annotated.json, N = 21)
n8n_workflows/     Flujos de n8n para generar y codificar historias
infrastructure/    Docker Compose y Dockerfile del análisis
results/           Salidas de n8n por modelo (llm_text/, human_text/) y resultados del análisis
scripts_test/      Verificación en Python (opcional)
```

## Licencia

MIT.
