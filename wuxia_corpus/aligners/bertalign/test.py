from bertalign import Bertalign
import re
import time
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


    return text_ch, text_en


text_ch, text_en = load_and_clean_text('awe_ch.txt', 'awe_en.txt')
print("cargado")
total_start = time.perf_counter()

aligner = Bertalign(text_ch, text_en)



aligner.align_sents()


total_elapsed = time.perf_counter() - total_start
print(f"Proceso completado. Tiempo total: {total_elapsed:.2f}s con segmentos alineados.")