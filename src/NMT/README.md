# NMT — Módulo de Traducción Automática Neuronal

## Organización

```
src/NMT/
  configs/
    __init__.py
    config.py                # @dataclass config base y específicas
    marianmt.py / m2m100.py / mbart.py / mt5.py / small100.py

  utils/
    __init__.py
    constants.py             # DEVICE, EOS_TOKEN_ID, PAD_TOKEN_ID
    reproducibility.py       # set_seed, mixed precision context
    data.py                  # build_dataloader, select_fraction
    generation.py            # generate_text + métricas (BLEU, ChrF, TER, ROUGE-L, METEOR, COMET)

  scripts/
    train.py                 # Entrenamiento fine-tuning
    evaluate.py              # Evaluación con todas las métricas
    translate.py             # Inferencia batch sobre test set

  training/                  # Notebooks de fine-tuning (originales)
  evaluation/
    Notebooks/
      pretrain/              # Notebooks evaluación modelos preentrenados
      train/                 # Notebooks evaluación modelos fine-tuned
    translate/               # Salida fija de traducciones y resultados (.txt)
```

## Uso CLI

Ejecuta siempre desde la raíz del proyecto o desde `src/NMT/scripts/`.

```bash
# Entrenar
python src/NMT/scripts/train.py mbart --fraction 0.1 --epochs 2 --batch-size 8
python src/NMT/scripts/train.py m2m100 --fraction 1.0 --epochs 10
python src/NMT/scripts/train.py marianmt

# Evaluar (calcula BLEU, ChrF, TER, ROUGE-L, METEOR y COMET)
python src/NMT/scripts/evaluate.py mbart
python src/NMT/scripts/evaluate.py m2m100 --num-sentences 10

# Traducir test guardando en src/NMT/evaluation/translate/
python src/NMT/scripts/translate.py mbart --out-file mbart.txt --num-sentences 10
python src/NMT/scripts/translate.py marianmt --out-file marianmt_base.txt
```

## Rutas

- Los checkpoints se buscan en `models/{model_dir}/checkpoint-*`.
- El mejor modelo se guarda en `models/{model_dir}/best`.
- Las salidas de `translate.py` y `evaluate.py` van a `src/NMT/evaluation/translate/`.

### Si quieres importar desde un notebook:

```python
from NMT.configs.mbart import config
from NMT.utils.data import select_fraction
from NMT.utils.generation import generate_text
```
