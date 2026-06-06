# Corpus Processing Scripts Package
__version__ = "1.0.0"
__author__ = "TFG - Hugo Silvosa"

from scripts.common.config_loader import get_config, CorpusConfig
from scripts.common.utils import (
    setup_logging,
    load_text_file,
    save_text_file,
    get_file_pairs,
    clean_text,
    chunk_text
)

__all__ = [
    'get_config',
    'CorpusConfig',
    'setup_logging',
    'load_text_file',
    'save_text_file',
    'get_file_pairs',
    'clean_text',
    'chunk_text'
]
