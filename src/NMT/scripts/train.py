import argparse
import sys
from pathlib import Path
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    EarlyStoppingCallback,
)

sys.path.append(str(Path(__file__).resolve().parents[2]))

from NMT.utils.reproducibility import set_seed, enable_mixed_precision
from NMT.utils.data import build_dataloader, select_fraction
from NMT.utils.generation import decode_ids_to_text
from NMT.configs.config import (
    MarianMTConfig,
    M2M100Config,
    MBartConfig,
    MT5Config,
    BaseConfig,
)

MODEL_CONFIGS = {
    "marianmt": MarianMTConfig,
    "m2m100": M2M100Config,
    "mbart": MBartConfig,
    "mt5": MT5Config,
    "small100": BaseConfig,
}

MODEL_DIR_NAMES = {
    "marianmt": "marianmt_wuxia",
    "m2m100": "m2m100_wuxia",
    "mbart": "mbart50_wuxia",
    "mt5": "mt5_small",
    "small100": "small100_wuxia",
}


def load_dataset(cfg):
    try:
        from datasets import load_from_disk
        dataset = load_from_disk(str(cfg.dataset_dir))
        print(f"Dataset cargado: {dataset}")
        return dataset["train"], dataset["validation"], dataset["test"]
    except Exception as e:
        print(f"Error cargando dataset: {e}")
        raise


def preprocess(examples, tokenizer, cfg):
    inputs = [str(x) for x in examples[cfg.src_col]]
    targets = [str(x) for x in examples[cfg.tgt_col]]
    model_inputs = tokenizer(
        inputs, max_length=cfg.max_source_length, truncation=True, padding="max_length"
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets, max_length=cfg.max_target_length, truncation=True, padding="max_length"
        )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def train(args):
    cfg_cls = MODEL_CONFIGS[args.model]
    cfg = cfg_cls(
        dataset_dir=Path(args.dataset_dir),
        output_dir=Path(args.output_dir),
        model_ckpt=args.model_ckpt or cfg_cls.__dataclass_fields__["model_ckpt"].default,
        fraction=args.fraction,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
    set_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {device}")

    train_ds, val_ds, test_ds = load_dataset(cfg)
    train_ds = select_fraction(train_ds, cfg.fraction, cfg.seed)

    tokenizer = AutoTokenizer.from_pretrained(str(cfg.model_ckpt))
    if hasattr(cfg, "translation_prefix"):
        def add_prefix(example):
            example[cfg.src_col] = cfg.translation_prefix + str(example[cfg.src_col])
            return example
        train_ds = train_ds.map(add_prefix)
        val_ds = val_ds.map(add_prefix)
        test_ds = test_ds.map(add_prefix)

    train_tok = train_ds.map(lambda ex: preprocess(ex, tokenizer, cfg), batched=True)
    val_tok = val_ds.map(lambda ex: preprocess(ex, tokenizer, cfg), batched=True)

    model = AutoModelForSeq2SeqLM.from_pretrained(str(cfg.model_ckpt))
    model.to(device)

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(cfg.output_dir),
        num_train_epochs=cfg.epochs,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        learning_rate=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        predict_with_generate=True,
        fp16=(device == "cuda"),
        push_to_hub=False,
        logging_steps=100,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_tok,
        eval_dataset=val_tok,
        tokenizer=tokenizer,
        data_collator=data_collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=cfg.early_stopping_patience)],
    )

    print("Iniciando entrenamiento...")
    trainer.train()
    model.save_pretrained(cfg.output_dir / "best")
    tokenizer.save_pretrained(cfg.output_dir / "best")
    print(f"Modelo guardado en {cfg.output_dir / 'best'}")


def evaluate(args):
    from NMT.utils.generation import generate_text
    from NMT.utils.data import build_dataloader
    from torch.utils.data import DataLoader

    cfg = MODEL_CONFIGS[args.model](
        dataset_dir=Path(args.dataset_dir),
        output_dir=Path(args.output_dir),
        model_ckpt=args.checkpoint or MODEL_CONFIGS[args.model].__dataclass_fields__["model_ckpt"].default,
        fraction=args.fraction,
    )
    set_seed(cfg.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    _, _, test_ds = load_dataset(cfg)
    test_ds = select_fraction(test_ds, cfg.fraction, cfg.seed)

    tokenizer = AutoTokenizer.from_pretrained(str(cfg.checkpoint if args.checkpoint else cfg.model_ckpt))
    model = AutoModelForSeq2SeqLM.from_pretrained(str(cfg.checkpoint if args.checkpoint else cfg.model_ckpt))
    model.to(device)

    src_texts = [str(x[cfg.src_col]) for x in test_ds]
    ref_texts = [str(x[cfg.tgt_col]) for x in test_ds]

    preds = generate_text(
        model,
        tokenizer,
        src_texts,
        max_length=cfg.max_target_length,
        batch_size=cfg.batch_size,
    )

    from NMT.utils.generation import compute_rougeL_f1, compute_meteor
    rouge = compute_rougeL_f1(preds, ref_texts)
    meteor = compute_meteor(preds, ref_texts)
    print(f"ROUGE-L F1: {rouge:.4f}")
    print(f"METEOR: {meteor:.4f}")

    return rouge, meteor


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", choices=MODEL_CONFIGS.keys(), help="Model name")
    parser.add_argument("--dataset-dir", default=str(get_project_root() / "processed_data" / "wuxia_zh_en_clean"))
    parser.add_argument("--output-dir", default=str(get_project_root() / "models" / "wuxia_output"))
    parser.add_argument("--model-ckpt", default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--fraction", type=float, default=1.0)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)

    args, _ = parser.parse_known_args()

    if len(sys.argv) < 3:
        parser.print_help()
        return

    if "train" in sys.argv:
        train(args)
    elif "evaluate" in sys.argv or "eval" in sys.argv:
        evaluate(args)
    elif "translate" in sys.argv:
        evaluate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
