# NMT — Módulo de Traducción Automática Neuronal

## Organización

```
src/NMT/
  configs/
    __init__.py
    config.py                # @dataclass config base y específicas
    marianmt.py              # Config MarianMT
    m2m100.py                # Config M2M-100
    mbart.py                 # Config mBART
    mt5.py                   # Config mT5
    small100.py              # Config SMaLL-100

  utils/
    __init__.py
    constants.py             # DEVICE, EOS_TOKEN_ID, PAD_TOKEN_ID
    reproducibility.py       # set_seed, mixed precision context
    data.py                  # build_dataloader, select_fraction
    generation.py            # generate_text, decode_ids_to_text

  scripts/
    train.py                 # CLI: entrenamiento genérico por modelo
    evaluate.py              # CLI: evaluación con métricas
    translate.py             # CLI: inferencia batch sobre test set

  training/                  # Notebooks de fine-tuning (originales)
  evaluation/
    Notebooks/
      pretrain/              # Notebooks evaluación modelos preentrenados
      train/                 # Notebooks evaluación modelos fine-tuned
    translate/               # Traducciones generadas y logs
```

## Uso CLI

```bash
python src/NMT/scripts/translate.py mbart --out-file output.txt --num-sentences 10
python src/NMT/scripts/train.py mbart --fraction 0.1 --epochs 2
python src/NMT/scripts/evaluate.py mbart --checkpoint ...
```

## Validación

```bash
python src/NMT/scripts/train.py --model marianmt --fraction 0.1 --epochs 2
python src/NMT/scripts/evaluate.py --model small100 --fraction 0.1
```
