import pandas as pd
import numpy as np
import os
import sacrebleu
from sacrebleu.metrics import CHRF, TER
from rouge_score import rouge_scorer
from nltk.tokenize import wordpunct_tokenize
from nltk.translate.meteor_score import meteor_score
from bert_score import score as calc_bertscore
from comet import download_model, load_from_checkpoint
import nltk

# Asegurar descargas necesarias de NLTK
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
    nltk.download('omw-1.4')

# --- CONFIGURACIÓN DE MODELOS PESADOS ---
print("Cargando modelo COMET (puede tardar unos minutos la primera vez)...")
comet_model_path = download_model("Unbabel/wmt22-comet-da")
comet_model = load_from_checkpoint(comet_model_path)
print("Modelo COMET cargado.")

def compute_metrics(preds, refs):
    """
    Calcula las métricas de evaluación automática.
    preds: lista de strings (Traducciones generadas por el modelo).
    refs: lista de strings (Traducciones humanas de referencia -> Texto_Input).
    """
    if not preds or not refs or len(preds) != len(refs): 
        return {k: 0.0 for k in ["sacrebleu", "chrf2", "ter", "rougeL_f1", "meteor", "bertscore", "comet"]}
    
    # Métricas Clásicas
    bleu = sacrebleu.corpus_bleu(preds, [refs]).score
    chrf = CHRF(word_order=2).corpus_score(preds, [refs]).score
    ter = TER().corpus_score(preds, [refs]).score
    
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    rouge_avg = float(np.mean([scorer.score(r, h)['rougeL'].fmeasure for h, r in zip(preds, refs)])) * 100.0
    meteor_avg = float(np.mean([meteor_score([wordpunct_tokenize(r)], wordpunct_tokenize(h)) for h, r in zip(preds, refs)])) * 100.0
    
    # --- BERTSCORE ---
    # lang="en" porque estamos evaluando traducciones de Chino a Inglés
    print("  -> Calculando BERTScore...")
    _, _, F1 = calc_bertscore(preds, refs, lang="en", verbose=False)
    bertscore_avg = float(F1.mean()) * 100.0
    
    # --- COMET ---
    # src: texto en chino, mt: predicción del LLM, ref: referencia humana en inglés.
    print("  -> Calculando COMET...")
    comet_data = [{"src": r, "mt": p, "ref": r} for p, r in zip(preds, refs)]
    comet_output = comet_model.predict(comet_data, batch_size=8, progress_bar=False)
    comet_avg = float(comet_output.system_score) * 100.0
    
    return {
        "sacrebleu": round(bleu, 2), 
        "chrf2": round(chrf, 2), 
        "ter": round(ter, 2), 
        "rougeL_f1": round(rouge_avg, 2), 
        "meteor": round(meteor_avg, 2),
        "bertscore": round(bertscore_avg, 2),
        "comet": round(comet_avg, 2)
    }

def evaluar_traducciones(archivo_entrada="traducciones_modelos.txt", archivo_salida="resultados_automaticas.txt"):
    if not os.path.exists(archivo_entrada):
        print(f"Error: No se encontró el archivo '{archivo_entrada}'.")
        return

    print(f"\nLeyendo traducciones desde '{archivo_entrada}'...")
    
    try:
        # Leemos el CSV delimitado por punto y coma
        df = pd.read_csv(archivo_entrada, sep=";")
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
        return

    # Verificamos que las columnas clave existan
    columnas_necesarias = ['Modelo', 'Texto_Input', 'Traduccion_Raw']
    for col in columnas_necesarias:
        if col not in df.columns:
            print(f"Error crítico: Falta la columna '{col}' en el archivo de texto.")
            return

    resultados_finales = []
    modelos = df['Modelo'].unique()

    print(f"Modelos detectados para evaluar: {', '.join(modelos)}")
    
    for modelo in modelos:
        print(f"\nProcesando métricas para el modelo: {modelo.upper()}...")
        
        # Filtramos los datos de este modelo y eliminamos filas vacías
        df_modelo = df[df['Modelo'] == modelo].dropna(subset=['Traduccion_Raw', 'Texto_Input'])
        
        # Predicción = Lo que generó la IA (Traduccion_Raw)
        # Referencia = La traducción humana oficial (Texto_Input)
        preds = df_modelo['Traduccion_Raw'].astype(str).tolist()
        refs = df_modelo['Texto_Input'].astype(str).tolist()
        
        if not preds:
            print(f"  -> No hay datos válidos para evaluar en {modelo}.")
            continue
            
        metricas = compute_metrics(preds, refs)
        metricas['Modelo'] = modelo.upper()
        resultados_finales.append(metricas)

    # Convertimos los resultados a un DataFrame para guardarlos limpios
    df_resultados = pd.DataFrame(resultados_finales)
    
    # Reordenamos columnas para que 'Modelo' salga la primera
    cols = ['Modelo'] + [c for c in df_resultados.columns if c != 'Modelo']
    df_resultados = df_resultados[cols]

    # Guardamos la tabla en un archivo .txt
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write("=== RESULTADOS DE MÉTRICAS ===\n")
        f.write("="*75 + "\n\n")
        f.write(df_resultados.to_string(index=False))
        f.write("\n\n" + "="*75 + "\n")

    print(f"resultados en: {archivo_salida}")

if __name__ == "__main__":
    evaluar_traducciones('traducciones_modelos_old.txt', 'metricas_old.txt')