# LLM - Traducción Wuxia (Chino → Inglés)

Pipeline para inferencia y fine-tuning de modelos LLM en el dominio de la literatura wuxia china.

## Estructura

```
src/LLM/
├── cesga/                     # Scripts y jobs para HPC (CESGA)
│   ├── scripts/               # Scripts Python para ejecución en cluster
│   │   ├── gemma3.py                # Inferencia base Gemma3
│   │   ├── gemma_train.py           # Fine-tuning Gemma3 con LoRA
│   │   ├── llama3_train.py          # Fine-tuning Llama3
│   │   ├── qwen_train.py            # Fine-tuning Qwen
│   │   ├── glm_train.py             # Fine-tuning GLM
│   │   ├── gemma3_*.py              # Variantes Gemma3 (1b, 4b, 270m, 12b)
│   │   └── train_test.py            # Job de inferencia + benchmark
│   └── BATCH CESGA/         # Scripts SLURM (.sh) - subir a HPC
│       ├── gemma.sh, gemma_fine.sh
│       ├── llama_train.sh, llama.sh
│       ├── qwen*.sh, glm*.sh
│       └── yi.py
│
├── evaluation/                # Resultados y métricas
│   ├── final/                 # Resultados finales de inferencia
│   │   ├── gemma3_base/finetuned.txt
│   │   ├── llama3_base/finetuned.txt
│   │   ├── glm_base/finetuned.txt
│   │   └── qwen3_base/finetuned.txt
│   ├── extra/                 # Resultados adicionales
│   ├── legacy/                # Resultados antiguos
│   ├── evaluation.py          # Evaluación (BLEU, METEOR, COMET, BERTScore)
│   ├── plot_metrics.py      # Gráficos de métricas
│   └── times.py             # Análisis de tiempos
│
├── notebook_local/            # Jupyter notebooks para desarrollo local
│   ├── gemma.ipynb, gemma3.ipynb
│   ├── llama-2.ipynb, llama-3.ipynb
│   ├── qwen.ipynb, qwen2-5.ipynb, qwen3.ipynb
│   ├── deepseek.py, yi.py
│   └── qi.ipynb
│
└── prompts.json               # Prompts de traducción (5 variantes)
```

## Uso

### Local (desarrollo)

```bash
cd src/LLM/notebook_local
# Ejecutar notebooks Jupyter
jupyter notebook
```

### HPC (CESGA)

1. Subir scripts y BATCH CESGA al cluster
2. Ejecutar jobs SLURM:

```bash
sbatch BATCH_CESGA/gemma.sh
sbatch BATCH_CESGA/gemma_fine.sh
```
