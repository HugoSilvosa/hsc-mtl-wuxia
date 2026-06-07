# preprocessing/ — Análisis estadístico y léxico del corpus Wuxia

Módulo de análisis del corpus paralelo chino→inglés del TFG. A partir del corpus
ya alineado, calcula métricas de riqueza léxica, extrae entidades del género
(facciones, técnicas, personajes) y genera figuras y grafos de co-ocurrencia.
Contrasta el **corpus principal** (novelas seleccionadas) con un **corpus de
referencia** de Hugging Face.

## Estructura

```
preprocessing/
├── inputs/                     # Datos fuente (entradas)
│   ├── corpus/                 #   corpus paralelo ZH-EN (formato "chino ; inglés")
│   │   ├── dataset.txt         #     corpus principal unificado
│   │   ├── final_awe.txt       #     A will Eternal
│   │   ├── final_condor_{1,2,3}.txt   # Condor (3 partes)
│   │   └── final_gu.txt        #     Gu Zhenren
│   └── scores/                 #   scores chrF por modelo NMT (selección de datos)
│       └── scores_*.csv
│
├── src/                        # Código
│   ├── analysis.py             #   análisis principal (métricas + figuras + grafos)
│   ├── merge.py                #   utilidad: unir .txt
│   ├── count.py                #   utilidad: contar palabras del corpus
│   └── preprocessing/          #   preparación del dataset HF
│       ├── preprocessing.py
│       ├── chapter_process.py
│       └── data_selection.py
│
├── outputs/                    # Resultados generados
│   ├── main/                   #   corpus principal
│   │   ├── statistics/         #     PNGs (riqueza, longitudes, Zipf, top entidades)
│   │   └── graphs/             #     grafos HTML por novela (AWE/CONDOR/GU) + GLOBAL
│   └── hf/                     #   corpus de referencia Hugging Face
│       ├── statistics/
│       └── graphs/
│
└── docs/
    └── analysis.md             # redacción de resultados (metodología + discusión)
```

## Uso

Las rutas de los scripts se resuelven respecto a `preprocessing/`, así que pueden
ejecutarse desde cualquier directorio:

```bash
# Análisis completo (corpus principal + dataset HF) → genera outputs/
python src/analysis.py

# Selección estratificada de muestras del dataset HF a partir de los scores chrF
python src/preprocessing/data_selection.py --mode study     # inspección
python src/preprocessing/data_selection.py --mode execute   # guarda el dataset

# Conteo rápido de palabras del corpus
python src/count.py
```

> `analysis.py` lee el dataset HF desde `../processed_data/wuxia_selected_100000`
> (ruta absoluta al inicio de la sección HF	).

## Dependencias

`matplotlib`, `seaborn`, `numpy`, `pandas`, `jieba`, `nltk`, `lexicalrichness`,
`pyvis`, `datasets`.
