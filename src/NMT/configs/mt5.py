from pathlib import Path
from .config import MT5Config

config = MT5Config(
    dataset_dir=Path("/ruta/a/processed_data/wuxia_zh_en_clean"),
    output_dir=Path("/ruta/a/models/mt5_small"),
    model_ckpt="google/mt5-small",
    use_instruction_prefix=True,
    translation_prefix="translate Chinese to English: ",
)
