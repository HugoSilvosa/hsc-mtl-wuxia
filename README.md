# TFG Hugo Silvosa Cuervo

**Enfoques de traducción automática con modelos de lenguaje en obras *wuxia***

## Requisitos

- Python 3.9+
- PyTorch, Transformers, sentence-transformers, datasets, nltk, jieba, lexicalrichness, pandas, numpy, matplotlib, seaborn, pyvis

```bash
pip install -r requirements.txt
```

## Estructura del Repositorio

```
TFG/
├── wuxia_corpus/              # Corpus wuxia: preprocesamiento y alineamiento
│   ├── src/
│   │   ├── preprocessing/     # Segmentación de capítulos (chino/inglés)
│   │   ├── alignment/         # Alineamiento LaBSE + programación dinámica
│   │   ├── analysis/          # Análisis de similitud coseno
│   │   └── common/            # Configuración y utilidades
│   └── data/                  # Datos raw, segmentados y procesados (AWE, CONDOR, GU, ISSTH)
│
├── preprocessing/             # Análisis léxico y estadístico del corpus (ver preprocessing/README.md)
│   ├── inputs/
│   │   ├── corpus/            # Corpus paralelo alineado (final_*.txt)
│   │   └── scores/            # Scores chrF para selección de datos
│   ├── src/                   # Código: analysis.py, merge.py, count.py, preprocessing/
│   └── outputs/               # Estadísticas (PNGs), grafos (HTML) - principal y HuggingFace
│
├── src/
│   ├── NMT/                   # Modelos NMT: mBART50, M2M100, MarianMT, mT5, Small100
│   │   ├── configs/           # Configuraciones por modelo
│   │   ├── utils/             # helpers, métricas, data loaders
│   │   └── scripts/           # train.py, evaluate.py, translate.py
│   ├── LLM/                   # Modelos LLM: Gemma, Llama, Qwen, GLM, Yi, DeepSeek (ver src/LLM/README.md)
│   │   ├── cesga/             # Scripts y jobs SLURM para HPC
│   │   ├── evaluation/        # Resultados, métricas, gráficos, tiempos
│   │   └── notebook_local/    # Notebooks Jupyter para desarrollo local
│   └── SMT/                   # Statistical Machine Translation
│       ├── smt_test.py        # Pruebas SMT
│       └── smt_prob.py        # Probabilidades SMT
│
├── models/                    # Modelos fine-tuned y checkpoints
│   ├── mbart50_wuxia/
│   ├── m2m100_wuxia/
│   ├── marianmt_wuxia/
│   └── mt5_small/
│
├── processed_data/            # Datasets procesados para entrenamiento
│   ├── wuxia_zh_en_clean/     # Corpus principal limpio
│   ├── wuxia_selected_100000/   # Muestra estratificada (100k pares) usada para el TFG
│   └── chapter_data/, chunk_data/ # Variantes preprocesadas
│
├── evaluation/                # Evaluación: CO2, métricas cualitativas, tiempos
│   ├── CO2/
│   ├── cualitativa/           # Evaluación cualitativa: LLM as JUDGE
│   └── times/
│
├── figures/                   # Diagramas (arquitecturas, BPE, segmentación) del TFG
│   └── graficas/, llm/, NMT/
│
├── images/                    # Portadas de libros, diagramas Gantt
│
├── logs/                      # Logs de entrenamiento y ejecución
│
└── docs/                      # Documentación (memoria, anteproyecto)
```

## Pipeline General

```
1. Construcción del corpus
   ↓
   wuxia_corpus/ → Segmentación y alineamiento Chino-Inglés (AWE, CONDOR, GU, ISSTH)

2. Análisis y preparación del dataset
   ↓
   preprocessing/ → Métricas léxicas, selección de datos, generación de splits

3. Experimentos de traducción
   ↓
   src/
   ├── SMT/   → Statistical Machine Translation (baseline)
   ├── NMT/   → Neural Machine Translation (mBART50, M2M100, MarianMT, mT5, Small100)
   └── LLM/   → Large Language Models (Gemma, Llama, Qwen, GLM, Yi, DeepSeek)

4. Evaluación y resultados
   ↓
   evaluation/
   ├── CO2/         → Métricas de huella de carbono
   ├── times/       → Análisis de tiempos de inferencia
   └── cualitativa/ → Evaluación cualitativa (LLMs-as-judge)
```

### wuxia_corpus/

Herramientas para crear el corpus paralelo chino-inglés:

- **preprocessing/chinese.py** - Segmentación de capítulos en chino
- **preprocessing/english.py** - Segmentación de capítulos en inglés
- **alignment/final_*.py** - Alineamiento con embeddings LaBSE
- Ver `wuxia_corpus/README.md` para detalles

### preprocessing/

Análisis léxico del corpus alineado:

```bash
python preprocessing/src/analysis.py
python preprocessing/src/count.py
```

### src/SMT/

Baseline estadístico:

```bash
python src/SMT/smt_test.py
python src/SMT/smt_prob.py
```

### src/NMT/

Modelos de traducción neuronal:

```bash
python src/NMT/scripts/train.py m2m100 --fraction 0.1 --epochs 3
python src/NMT/scripts/evaluate.py m2m100
python src/NMT/scripts/translate.py m2m100 --out-file m2m100.txt
```

### src/LLM/

Fine-tuning e inferencia (ver src/LLM/README.md):

```bash
# Local (notebooks)
cd src/LLM/notebook_local && jupyter notebook

# HPC (CESGA)
sbatch src/LLM/cesga/BATCH\ CESGA/gemma.sh
sbatch src/LLM/cesga/BATCH\ CESGA/gemma_fine.sh
```

### evaluación/

- **CO2/** - Métricas de emisiones de carbono por modelo
- **cualitativa/** - Evaluación con LLMs como jueces (archivos evaluados/separados)
- **times/** - Análisis de latencia y rendimiento

| Nombre | Descripción                  | Origen           |
| ------ | ----------------------------- | ---------------- |
| AWE    | A Will of Eternal             | novela wuxia     |
| CONDOR | The Condor Trilogy (Jin Yong) | 3 volúmenes     |
| GU     | Guzhenren novels              | colección wuxia |
| ISSTH  | I Shall Seal the Heavens      | wuxia/xianxia    |

## Resultados

Las métricas completas y gráficos están en `preprocessing/outputs/` y `evaluation/`.
