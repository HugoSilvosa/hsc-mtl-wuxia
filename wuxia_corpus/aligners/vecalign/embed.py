# Requiere: pip install sentence-transformers numpy
from sentence_transformers import SentenceTransformer
import numpy as np
import sys

# Usamos LaBSE, que es excelente para Chino-Inglés
model = SentenceTransformer('sentence-transformers/LaBSE')

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f.readlines()]

# Generar embeddings
embeddings = model.encode(lines)

# Guardar en formato binario float32 (lo que Vecalign espera)
with open(output_file, 'wb') as f:
    embeddings.astype(np.float32).tofile(f)