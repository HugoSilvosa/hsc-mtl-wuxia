from pathlib import Path
from .config import MarianMTConfig

config = MarianMTConfig(
    dataset_dir=Path("/ruta/a/processed_data/wuxia_zh_en_clean"),
    output_dir=Path("/ruta/a/models/marianmt_wuxia"),
    model_ckpt="Helsinki-NLP/opus-mt-zh-en",
)
