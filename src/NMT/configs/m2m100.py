from pathlib import Path
from .config import M2M100Config

config = M2M100Config(
    dataset_dir=Path("/ruta/a/processed_data/wuxia_zh_en_clean"),
    output_dir=Path("/ruta/a/models/m2m100_wuxia"),
    model_ckpt="facebook/m2m100_418M",
)
