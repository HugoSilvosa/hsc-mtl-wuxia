from pathlib import Path
from .config import BaseConfig

config = BaseConfig(
    dataset_dir=Path("/ruta/a/processed_data/wuxia_zh_en_clean"),
    output_dir=Path("/ruta/a/models/small100_wuxia"),
    model_ckpt="alirezamsh/small100",
)
