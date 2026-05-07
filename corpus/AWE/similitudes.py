import os
from sentence_transformers import SentenceTransformer, util

# --- CONFIGURACIÓN ---
INPUT_FILE_1 = "gu10.txt"    # El formato: Chino ; Inglés
INPUT_FILE_2 = "gu_ch10.txt"  # El formato de 3 líneas
OUTPUT_FILE = "resultados_similitud100.txt"  
FILTER_THRESHOLD = 0.15                  

print("Cargando modelo LaBSE...")
model = SentenceTransformer('sentence-transformers/LaBSE')

def clean_text_for_csv(text):
    """Limpia el texto para respetar el formato CSV con ;"""
    if not text:
        return ""
    text = text.replace('\n', ' ').replace('\r', '')
    text = text.replace(';', ',') 
    return text.strip()

def calculate_similarity(text1, text2):
    """Calcula la similitud coseno."""
    if not text1.strip() or not text2.strip():
        return 0.0
    
    embeddings1 = model.encode(text1, convert_to_tensor=True)
    embeddings2 = model.encode(text2, convert_to_tensor=True)
    return util.pytorch_cos_sim(embeddings1, embeddings2).item()

def print_stats(total_score, total_count, filtered_score, filtered_count, filename):
    """Función auxiliar para imprimir las estadísticas en consola"""
    print(f"\n--- Estadísticas para: {filename} ---")
    
    # 1. Media Global (Todo el contenido)
    if total_count > 0:
        avg_total = total_score / total_count
        print(f"   [GLOBAL]")
        print(f"   > Total frases procesadas: {total_count}")
        print(f"   > Media de similitud:      {avg_total:.4f}")
    else:
        print("   > No hay frases para procesar.")

    # 2. Media Filtrada (Solo lo útil)
    if filtered_count > 0:
        avg_filtered = filtered_score / filtered_count
        print(f"   [FILTRADO (Similitud >= {FILTER_THRESHOLD})]")
        print(f"   > Frases que pasan el filtro: {filtered_count} (de {total_count})")
        print(f"   > Media filtrada:             {avg_filtered:.4f}")
    else:
        print(f"   [FILTRADO] Ninguna frase superó el umbral de {FILTER_THRESHOLD}")

def process_files():
    with open(OUTPUT_FILE, 'w', encoding='utf-8-sig') as out_f:
        out_f.write("archivo;chino;ingles;similitud\n")

        # ---------------------------------------------------------
        # PROCESAMIENTO ARCHIVO 1
        # ---------------------------------------------------------
        if os.path.exists(INPUT_FILE_1):
            print(f"Procesando {INPUT_FILE_1}...")
            with open(INPUT_FILE_1, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Variables para media GLOBAL
            total_score = 0.0
            total_count = 0
            
            # Variables para media FILTRADA
            filtered_score = 0.0
            filtered_count = 0

            for line in lines:
                line = line.strip()
                if not line: continue

                parts = line.split(';')
                if len(parts) >= 2:
                    raw_zh = parts[0]
                    raw_en = ";".join(parts[1:])
                    
                    score = calculate_similarity(raw_zh, raw_en)
                    
                    # Actualizar Globales
                    total_score += score
                    total_count += 1
                    
                    # Actualizar Filtrados (Si supera el umbral)
                    if score >= FILTER_THRESHOLD:
                        filtered_score += score
                        filtered_count += 1
                    
                    out_zh = clean_text_for_csv(raw_zh)
                    out_en = clean_text_for_csv(raw_en)
                    out_f.write(f"{INPUT_FILE_1};{out_zh};{out_en};{score:.5f}\n")
            
            # Imprimir reporte
            print_stats(total_score, total_count, filtered_score, filtered_count, INPUT_FILE_1)

        else:
            print(f"Aviso: No se encontró {INPUT_FILE_1}")

        # ---------------------------------------------------------
        # PROCESAMIENTO ARCHIVO 2
        # ---------------------------------------------------------
        if os.path.exists(INPUT_FILE_2):
            print(f"Procesando {INPUT_FILE_2}...")
            with open(INPUT_FILE_2, 'r', encoding='utf-8') as f:
                raw_lines = f.read().splitlines()

            total_score = 0.0
            total_count = 0
            filtered_score = 0.0
            filtered_count = 0

            for i in range(0, len(raw_lines), 3):
                if i + 1 >= len(raw_lines):
                    break
                
                raw_zh = raw_lines[i]
                raw_en = raw_lines[i+1]

                score = calculate_similarity(raw_zh, raw_en)
                
                # Actualizar Globales
                total_score += score
                total_count += 1
                
                # Actualizar Filtrados
                if score >= FILTER_THRESHOLD:
                    filtered_score += score
                    filtered_count += 1
                
                out_zh = clean_text_for_csv(raw_zh)
                out_en = clean_text_for_csv(raw_en)
                out_f.write(f"{INPUT_FILE_2};{out_zh};{out_en};{score:.5f}\n")

            # Imprimir reporte
            print_stats(total_score, total_count, filtered_score, filtered_count, INPUT_FILE_2)

        else:
            print(f"Aviso: No se encontró {INPUT_FILE_2}")

    print(f"\n--- Finalizado. Detalles guardados en: {OUTPUT_FILE} ---")

if __name__ == "__main__":


    process_files()