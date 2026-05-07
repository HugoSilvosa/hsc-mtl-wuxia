import argparse
import random
import unicodedata
from pathlib import Path
import pandas as pd
from datasets import Dataset, DatasetDict
import string

# Lista de puntuación a conservar
ALLOWED_PUNCT = set(string.punctuation) | {"，", "。", "！", "？", "、", "；", "：", "“", "”", "‘", "’", "—", "…"}

def is_letter_or_mark(ch: str) -> bool:
    cat = unicodedata.category(ch)
    return cat[0] in ("L", "M")

def is_space(ch: str) -> bool:
    return unicodedata.category(ch) == "Zs" or ch in [" ", "\t"]

def is_allowed_punct(ch: str) -> bool:
    return ch in ALLOWED_PUNCT

def clean_text(s: str) -> str:
    if not s:
        return ""
    kept = []
    for ch in s:
        if is_letter_or_mark(ch) or is_space(ch) or is_allowed_punct(ch):
            kept.append(ch)
    out = "".join(kept)

    # Quitar puntuación al inicio y final
    while out and is_allowed_punct(out[0]):
        out = out[1:]
    while out and is_allowed_punct(out[-1]):
        out = out[:-1]

    # Normalizar espacios
    out = " ".join(out.split())

    if all(is_allowed_punct(ch) or is_space(ch) for ch in out):
        return ""

    return out.strip()

def load_and_group(input_path: Path, sep=";", chunk_size=5):
    valid_pairs = []
    
    # 1. Leer todas las líneas válidas y limpiarlas
    with input_path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or sep not in line:
                continue
            
            # Separar por el primer ";" que encuentre
            left, right = line.split(sep, 1)
            zh_raw = left.strip()
            en_raw = right.strip()
            
            zh = clean_text(zh_raw)
            en = clean_text(en_raw)
            
            if not zh or not en:
                continue
                
            valid_pairs.append((zh, en))
            
    # 2. Agrupar las líneas en bloques de tamaño "chunk_size"
    srcs, tgts = [], []
    for i in range(0, len(valid_pairs), chunk_size):
        chunk = valid_pairs[i : i + chunk_size]
        
        # Unimos las frases del bloque con un salto de línea
        zh_joined = ". ".join([p[0] for p in chunk])
        en_joined = ". ".join([p[1] for p in chunk])
        
        srcs.append(zh_joined)
        tgts.append(en_joined)
        
    return pd.DataFrame({"zh": srcs, "en": tgts})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_txt", type=str, required=True, help="Ruta a tu archivo .txt")
    parser.add_argument("--output_dir", type=str, required=True, help="Ruta donde se guardará el dataset")
    parser.add_argument("--chunk_size", type=int, default=5, help="Número de frases a juntar por bloque")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val_size", type=float, default=0.1)
    parser.add_argument("--test_size", type=float, default=0.1)
    args = parser.parse_args()

    random.seed(args.seed)

    input_path = Path(args.input_txt)
    df = load_and_group(input_path, sep=";", chunk_size=args.chunk_size)

    if len(df) < 5:
        raise ValueError("El dataset tiene muy pocos bloques tras la limpieza. Prueba a reducir el chunk_size.")

    # Mezclar el dataframe de bloques
    df = df.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)

    # --- Imprimir ejemplos ---
    print("\n" + "="*60)
    print(f"MUESTRA DE DATOS PROCESADOS (Bloques de {args.chunk_size} frases):")
    print("="*60)
    num_ejemplos = min(2, len(df)) # Mostramos 2 ejemplos para no saturar la pantalla
    for i in range(num_ejemplos):
        print(f"\n[BLOQUE EJEMPLO {i+1}]")
        print(">>> CHINO (ZH):")
        print(df.iloc[i]['zh'])
        print("\n>>> INGLÉS (EN):")
        print(df.iloc[i]['en'])
        print("-" * 40)
    print("="*60 + "\n")

    # Divisiones train/val/test
    n = len(df)
    n_test = int(n * args.test_size)
    n_val = int(n * args.val_size)
    n_train = n - n_test - n_val

    train_df = df.iloc[:n_train].reset_index(drop=True)
    val_df   = df.iloc[n_train:n_train + n_val].reset_index(drop=True)
    test_df  = df.iloc[n_train + n_val:].reset_index(drop=True)

    ds = DatasetDict(
        train=Dataset.from_pandas(train_df),
        validation=Dataset.from_pandas(val_df),
        test=Dataset.from_pandas(test_df),
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ds.save_to_disk(str(out_dir))
    
    print(f"Dataset guardado en: {out_dir}")
    print(f"Total de bloques generados: {n} (aprox. {n * args.chunk_size} frases procesadas)")
    print({k: len(v) for k, v in ds.items()})

if __name__ == "__main__":
    main()
    
        # python chapter_process.py --input_txt C:\Users\Usuario\Desktop\TFG\CORPUS\data\dataset.txt --output_dir C:\Users\Usuario\Desktop\TFG\CORPUS\processed_data\chunk_data