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
   ├── context/               # Modelos locales (opcional)
   ├── corpus/             # Jupyter notebooks
   ├── data/               # Se guardan los datasets individuales de cada libro y se juntan en uno final.
   ├── evaluation/
   ├── figures/
   ├── models/
   ├── preprocessing/      # Contiene preprocessing.py, que convierte el dataset (en txt) a un dataset de HugginFace.
   ├── processed_data/     # Contiene la carpeta `wuxia_zh_en_clean`, dataset usado en el proyecto
   ├── training
   ├──
   ├──
   ├──
   └── README.md              # Este archivo
   ```

##  CORPUS

En la carpeta `corpus` se encuentra el proceso de preparación y segmentación de los libros usados para la creación del dataset. 
Con 3 carpetas de libros (`AWE`, `CONDOR` y `GU`), una carpeta `ORIGINAL` donde se guardan los documentos originales, y un `TEST` de pruebas varias.

En AWE, se usan `chinese.py` y `english.py` para segmentar el libro en capitulos, y posteriormente se usa `final_awe.py` para segmentar los capitulos en segmentos.
En GU y CONDOR se sigue la misma ruta, teniendo en cuenta que CONDOR son 3 libros (trilogía).

Cada libro tiene sus propias características, por eso aunque la estructura es la misma, hubo que hacer modificaciones específicas al código que lee y segmenta cada libro.


