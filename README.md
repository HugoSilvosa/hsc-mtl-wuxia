# TFG Hugo Silvosa Cuervo


##  Requisitos

- Python 3.9+


Instalar dependencias:

```bash
pip install 
```

##  Configuración


1. **Estructura de carpetas:**
   ```
   .
   ├── corpus/             # Preparación y segmentación de los libros para crear el corpus paralelo
   ├── preprocessing/      # Análisis estadístico/léxico del corpus y selección de datos (ver preprocessing/README.md)
   ├── processed_data/     # Datasets procesados (p. ej. `wuxia_zh_en_clean`, usado en el proyecto)
   ├── src/                # Código de los modelos de traducción: LLM, NMT y SMT
   ├── models/             # Modelos entrenados (mBART50, M2M100, MarianMT, mT5, IBM…)
   ├── evaluation/         # Evaluación de los modelos (CO2, LLM, NMT, tiempos, cualitativa)
   ├── figures/            # Diagramas del TFG (arquitecturas, BPE, segmentación…)
   ├── images/             # Imágenes (portadas de los libros, diagrama de Gantt…)
   ├── logs/               # Logs de entrenamiento
   ├── docs/               # Documentación del TFG (memoria, anteproyecto, diario)
   └── README.md           # Este archivo
   ```

##  CORPUS

En la carpeta `corpus` se encuentra el proceso de preparación y segmentación de los libros usados para la creación del dataset. 
Con 3 carpetas de libros (`AWE`, `CONDOR` y `GU`), una carpeta `ORIGINAL` donde se guardan los documentos originales, y un `TEST` de pruebas varias.

En AWE, se usan `chinese.py` y `english.py` para segmentar el libro en capitulos, y posteriormente se usa `final_awe.py` para segmentar los capitulos en segmentos.
En GU y CONDOR se sigue la misma ruta, teniendo en cuenta que CONDOR son 3 libros (trilogía).

Cada libro tiene sus propias características, por eso aunque la estructura es la misma, hubo que hacer modificaciones específicas al código que lee y segmenta cada libro.


