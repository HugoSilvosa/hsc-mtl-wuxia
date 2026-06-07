import torch
from torch.utils.data import DataLoader
from tqdm.auto import tqdm


def generate_text(
    model,
    tokenizer,
    texts,
    max_length: int = 128,
    num_beams: int = 4,
    batch_size: int = 8,
):
    device = next(model.parameters()).device
    model.eval()
    preds = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Generating"):
        batch = texts[i : i + batch_size]
        encoded = tokenizer(
            batch, return_tensors="pt", padding=True, truncation=True, max_length=max_length
        ).to(device)
        with torch.no_grad():
            generated_ids = model.generate(
                **encoded,
                max_length=max_length,
                num_beams=num_beams,
            )
        preds.extend(tokenizer.batch_decode(generated_ids, skip_special_tokens=True))
    return preds


def decode_ids_to_text(dataset, id_col: str):
    return [row[id_col] for row in dataset]
