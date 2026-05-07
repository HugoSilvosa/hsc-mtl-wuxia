
import os
import re
import time
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import words
# nltk.download('punkt')  
import contractions





def get_device():
    """
    Retorna el dispositivo disponible: GPU (cuda) si existe, o CPU en caso contrario.
    """
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')




# Configura el modelo LaBSE para ejecutarse en GPU si está disponible
device = get_device()
print(f"Usando dispositivo: {device}")
model = SentenceTransformer('sentence-transformers/LaBSE', device=str(device))


def list_file_pairs(input_dir="."):
    """
    Busca y empareja archivos .ch.txt y .en.txt con el mismo prefijo numérico.
    
    Args:
        input_dir (str): Directorio donde buscar los archivos.
    
    Returns:
        list of tuple: Lista de tuplas (path_chino, path_ingles)
    """
    files = os.listdir(input_dir)
    en_files = {}
    ch_files = {}

    for f in files:
        match = re.match(r"(\d+)(en|ch)\.txt", f)
        if match:
            num, lang = match.groups()
            idx = int(num)
            if lang == 'en':
                en_files[idx] = os.path.join(input_dir, f)
            else:
                ch_files[idx] = os.path.join(input_dir, f)

    # solo empareja si ambos existen
    keys = sorted(set(en_files) & set(ch_files))
    return [(ch_files[k], en_files[k]) for k in keys]

def fix_broken_words(text):
    """
    Para palabras que en el textro original vienen rotas, "F ang", "c ultivation", se corrigen.

    Args:
        text (str): texto roto

    Returns:
        texto: texto limpio
    """
    # detecta letra + palabra
    pattern = re.compile(r'\b([a-zA-Z])\s+([a-z]{1,})\b')

    # palabras que si son válidas solas no deben unirse 
    no_merge_heads = {'a', 'i', 'he', 'she', 'we', 'you', 'it', 'an'}
    
    text = contractions.fix(text)
    
    text = re.sub(r"\b(\w+)[’']s\b(?=\s|$)", r"\1", text)            
            
    def merge_if_valid(match):
        head = match.group(1).lower()
        tail = match.group(2).lower()
        merged = head + tail
        if head in no_merge_heads:
            return match.group(0)  
        if merged in word_set:
            return merged
        return match.group(0)

    prev = ""
    while prev != text:
        prev = text
        text = pattern.sub(merge_if_valid, text)
    return text

def load_and_clean_text(path_ch, path_en):
    """
    Carga y limpia textos chino y ingles desde sus respectivos archivos.
    
    Elimina líneas vacías, paréntesis, notas y referencias numéricas.
    
    Args:
        path_ch (str): Ruta del archivo chino.
        path_en (str): Ruta del archivo ingles.
    
    Returns:
        tuple: Texto chino limpio, texto ingles limpio.
    """
    #  texto chino
    lines_ch = []
    with open(path_ch, 'r', encoding='utf-8', errors='ignore') as fch:
        for line in fch:
            s = line.lstrip()
            if not s or s.startswith('(') or s.startswith('（'):
                continue  # omite líneas vacías o con notas
            s = s.replace("&amp;amp; {}", "").strip()  # quita secuencia HTML raras
            lines_ch.append(s)
    text_ch = " ".join(lines_ch)
    text_ch = re.sub(r'（[^）]*）', '', text_ch)  # elimina notas entre paréntesis chinos

    #  texto ingles
    lines_en = []
    with open(path_en, 'r', encoding='utf-8', errors='ignore') as fen:
        for line in fen:
            s = line.lstrip()
            if not s or s.startswith('('):
                continue  # omite líneas vacías o notas
            cleaned = re.sub(r"\(\d+\)", "", line).strip()  # quita referencias tipo (1)
            cleaned = re.sub(r"\s{2,}", " ", cleaned)  # normaliza espacios múltiples
            lines_en.append(cleaned)
    text_en = " ".join(lines_en)
    text_en = fix_broken_words(text_en)

    return text_ch, text_en



def split_quotes(text: str, quote_chars: str):
    """
    Separa el texto en torno a cada comilla de `quote_chars`,
    dejando siempre la comilla como token independiente.
    """
    # captura cada comilla (ASCII o Unicode)
    pattern = f"([{re.escape(quote_chars)}])"
    parts = re.split(pattern, text)
    # filtra strings vacíos
    return [p for p in parts if p]

def segment_text(text_ch: str, text_en: str):
    """
    Segmenta el chino y el inglés de forma agresiva:
    - Separa por puntuación.
    - Elimina las comillas (“ ” ").
    """
    quote_chars = '"“”‘’\''
    
    
    
    
    
    # segmentacion chino
    ch_tokens = split_quotes(text_ch, quote_chars)
    segments_ch = []
    for tok in ch_tokens:
        if tok in quote_chars:
            continue  
        subs = re.split(r'(?<=[。！？；：:])', tok)
        segments_ch.extend([s.strip() for s in subs if s.strip()])

    # segmentacion ingles
    en_tokens = split_quotes(text_en, quote_chars)
    segments_en = []
    for tok in en_tokens:
        if tok in quote_chars:
            continue 
        for sent in sent_tokenize(tok):
            subs = re.split(r'(?<=[\.!\?:;])\s+', sent)
            segments_en.extend([s.strip() for s in subs if s.strip()])

    return segments_ch, segments_en


def get_embeddings(texts):
    """
    Devuelve embeddings para una lista de textos, usando caché para evitar
    recomputar repeticiones entre archivos.

    Args:
        texts (list of str): Lista de textos.

    Returns:
        np.ndarray: Embeddings de los textos en el mismo orden.
    """
    to_compute = []
    computed_indices = []

    # Identificar textos no cacheados
    for i, text in enumerate(texts):
        if text not in embedding_cache:
            to_compute.append(text)
            computed_indices.append(i)

    # Codificar solo los que no están en caché
    if to_compute:
        new_embeds = model.encode(to_compute, normalize_embeddings=True)
        for idx, text in zip(computed_indices, to_compute):
            embedding_cache[text] = new_embeds[idx - computed_indices[0]]

    # Recuperar embeddings en orden original
    return np.array([embedding_cache[text] for text in texts])


def align_segments(segments_ch, segments_en):
    """
    Alinea segmentos de texto en chino y ingles usando embeddings de LaBSE
    y programación dinámica.


    El algoritmo busca la mejor correspondencia entre pares de segmentos basándose
    en la similitud de coseno entre sus embeddings. Considera los siguientes emparejamientos:
    
    - 1-1: un segmento chino con uno ingles
    - 1-2: un segmento chino con dos segmentos ingleses
    - 2-1: dos segmentos chinos con uno ingles
    - 1-3: un segmento chino con tres segmentos ingleses
    - 3-1: tres segmentos chinos con un segmento ingles
    - Saltos (omisiones) penalizados

    Args:
        segments_ch (list): Lista de segmentos en chino.
        segments_en (list): Lista de segmentos en ingles.

    Returns:
        list of tuple: Lista alineada de pares (segmento_ch, segmento_es).
    """

    # Generar embeddings normalizados
    
    vecs_ch = model.encode(segments_ch, normalize_embeddings=True)    # Segmentos individuales (chino)
    vecs_en = model.encode(segments_en, normalize_embeddings=True)    # Segmentos individuales (ingles)

    M, N = len(segments_ch), len(segments_en)  # Longitudes de las listas

    # Generar embeddings para pares combinados de segmentos (2-1 y 1-2)
    vecs_ch2 = None
    vecs_en2 = None
    vecs_ch3 = None
    vecs_en3 = None
    
    if M > 1:
        combined_ch_segments = [segments_ch[i] + " " + segments_ch[i+1] for i in range(M-1)]
        vecs_ch2 = model.encode(combined_ch_segments, normalize_embeddings=True)
    if N > 1:
        combined_en_segments = [segments_en[j] + " " + segments_en[j+1] for j in range(N-1)]
        vecs_en2 = model.encode(combined_en_segments, normalize_embeddings=True)

    if M > 2:
        combined_ch_segments_3 = [segments_ch[i] + " " + segments_ch[i+1] + " " + segments_ch[i+2] for i in range(M-2)]
        vecs_ch3 = model.encode(combined_ch_segments_3, normalize_embeddings=True)
        
    if N > 2:
        combined_en_segments_3 = [segments_en[j] + " " + segments_en[j+1] + " " + segments_en[j+2] for j in range(N-2)]
        vecs_en3 = model.encode(combined_en_segments_3, normalize_embeddings=True)

    # Matrices de similitud por tipo
    sim_1to1 = np.dot(vecs_ch, vecs_en.T)         # Similaridad 1-1
    sim_1to2 = np.dot(vecs_ch, vecs_en2.T) if vecs_en2 is not None else None  # 1 chino : 2 ingles
    sim_2to1 = np.dot(vecs_ch2, vecs_en.T) if vecs_ch2 is not None else None  # 2 chinos : 1 ingles
    sim_1to3 = np.dot(vecs_ch, vecs_en3.T) if vecs_en3 is not None else None # 1-3
    sim_3to1 = np.dot(vecs_ch3, vecs_en.T) if vecs_ch3 is not None else None # 3-1
    
    # Matriz de dinamic programing
    DP = np.full((M+1, N+1), -1e9)  # Matriz con valores mínimos iniciales
    DP[0][0] = 0.0                  # Estado base: valor 0

    backpointer = [[None]*(N+1) for _ in range(M+1)]  # Guarda el camino óptimo

    
    # llenado de la tabla DP
    for i in range(M+1):  # para cada posición en chino
        for j in range(N+1):  # para cada posición en ingles

            # Caso 1-1: alineación directa
            if i > 0 and j > 0:
                score = DP[i-1][j-1] + sim_1to1[i-1, j-1]
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("1-1", i-1, j-1)

            # Caso 1-2: una chino, dos inglesas
            if i > 0 and j > 1 and sim_1to2 is not None:
                score = DP[i-1][j-2] + sim_1to2[i-1, j-2]
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("1-2", i-1, j-2)

            # Caso 2-1: dos chinas, una ingles
            if i > 1 and j > 0 and sim_2to1 is not None:
                score = DP[i-2][j-1] + sim_2to1[i-2, j-1]
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("2-1", i-2, j-1)
            
            # Caso 1-3: un china, tres ingles

            if i > 0 and j > 2 and sim_1to3 is not None:
                score = DP[i-1][j-3] + sim_1to3[i-1, j-3]
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("1-3", i-1, j-3)
            
            # Caso 3-1: tres chinas, una ingles

            if i > 2 and j > 0 and sim_3to1 is not None:
                score = DP[i-3][j-1] + sim_3to1[i-3, j-1]
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("3-1", i-3, j-1)
                    
            # Salto de segmento chino 
            if i > 0:
                score = DP[i-1][j] + skip_penalty
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("skip_ch", i-1, j)

            # Salto de segmento ingles 
            if j > 0:
                score = DP[i][j-1] + skip_penalty
                if score > DP[i][j]:
                    DP[i][j] = score
                    backpointer[i][j] = ("skip_en", i, j-1)

    
    # se reconstruye el mejor alineamiento    
    aligned = []
    i, j = M, N  #  desde la última celda

    while i > 0 or j > 0:
        action, pi, pj = backpointer[i][j]  # Recuperamos acción y coordenadas previas

        if action == "1-1":
            aligned.append((segments_ch[pi], segments_en[pj]))
            i, j = pi, pj

        elif action == "1-2":
            # Un segmento chino con dos ingleses
            combined_en = segments_en[pj] + ' ' + segments_en[pj+1]
            aligned.append((segments_ch[pi], combined_en))
            i, j = pi, pj

        elif action == "2-1":
            # Dos segmentos chinos con uno ingles
            combined_ch = segments_ch[pi] + ' ' + segments_ch[pi+1]
            aligned.append((combined_ch, segments_en[pj]))
            i, j = pi, pj

        elif action == "1-3":
            combined_en = segments_en[pj] + " " + segments_en[pj+1] + " " + segments_en[pj+2]
            aligned.append((segments_ch[pi], combined_en))
            i -= 1
            j -= 3
            
        elif action == "3-1":
            combined_ch = segments_ch[pi] + " " + segments_ch[pi+1] + " " + segments_ch[pi+2]
            aligned.append((combined_ch, segments_en[pj]))
            i -= 3
            j -= 1
            
        elif action == "skip_ch":
            i -= 1  # Saltamos segmento chino (no se alinea)

        else:  # action == "skip_en"
            j -= 1  # Saltamos segmento ingles (no se alinea)

    aligned.reverse()  # Invertimos para obtener el orden original
    return aligned



def labse_similarity(text1, text2):
    """
    Calcula la similitud de coseno entre dos textos usando LaBSE.
    """
    vec1, vec2 = get_embeddings([text1, text2])
    return float(np.dot(vec1, vec2.T))


def process_all_files(output, input_dir="."):
    """
    Procesa todos los archivos en el directorio: carga textos, segmenta en cláusulas optimizado,
    alinea una sola vez con embeddings multilingües y guarda el resultado.
    """
    pairs = list_file_pairs(input_dir)
    all_aligned = []

    with open(output, 'w', encoding='utf-8') as fout:
        for path_ch, path_en in pairs:
            print(f"Procesando par: {path_ch} + {path_en}")
            start = time.perf_counter()

            text_ch, text_en = load_and_clean_text(path_ch, path_en)
            seg_ch, seg_en = segment_text(text_ch, text_en)
            # Alineación inicial
            aligned = align_segments(seg_ch, seg_en)

            for ch_sub, en_sub in aligned:
                fout.write(f"{ch_sub} ; {en_sub}\n")

            elapsed = time.perf_counter() - start
            print(f"  Tiempo: {elapsed:.2f}s")
            all_aligned.extend(aligned)

    return all_aligned




# Bloque principal de ejecución
if __name__ == '__main__':
    
    
    # Configuración 
    ch_suffix = "ch.txt"
    en_suffix = "en.txt"
    
    skip_penalty = -0.5  # penalización por saltarse segmentos
    embedding_cache = {}  # Diccionario global: texto -> embedding
    
    # Palabras para corrección del texto
    word_set = set(words.words())



    for i in [1, 2, 3]:
        output_file = f"final_condor_{i}.txt"
        total_start = time.perf_counter()
        resultados = process_all_files(f"Chapter{i}\\.", out_file=output_file)
        total_elapsed = time.perf_counter() - total_start
        print(
            f"Proceso completado para Condor{i}. "
            f"Tiempo total: {total_elapsed:.2f}s con {len(resultados)} segmentos alineados."
        )