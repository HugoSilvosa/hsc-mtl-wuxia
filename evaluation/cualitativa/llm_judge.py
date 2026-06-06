import pandas as pd
import json
import os
import glob
import time
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

#  CONFIGURACIÓN DE API KEYS 
OPENAI_API_KEY = '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'
GEMINI_API_KEY = 'AIzaSyANweczz4t29Eg8Fk7ckMevipgaU3BarZ4'
ANTHROPIC_API_KEY = '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'

# Inicialización de clientes
cliente_openai = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
cliente_claude = Anthropic(api_key=ANTHROPIC_API_KEY)


USAR_GEMINI = True
USAR_OPENAI = True
USAR_CLAUDE = True

# FASE 1: PROMPTS Y FUNCIONES DE TRADUCCIÓN
def crear_prompt_traduccion(lote_json):
    return f"""
    Act as an expert Chinese-to-English translator specializing in Wuxia/Xianxia literature.
    Translate the following Chinese texts ('texto_raw') into ENGLISH.
    
    ABSOLUTE RULE: Provide ONLY the direct and pure translation. Do not explain, do not add notes.

    TEXTS TO TRANSLATE:
    {lote_json}

    OUTPUT INSTRUCTION:
    Return ONLY a valid JSON object.
    
    Exact expected format:
    {{
      "traducciones": [
        {{"id_temporal": 1, "traduccion_raw": "The sect master sighed deeply."}},
        {{"id_temporal": 2, "traduccion_raw": "The Qi energy flowed through his meridians."}}
      ]
    }}
    """

def ejecutar_traducciones_unicas(carpeta_entrada="archivos_separados", archivo_salida="traducciones_modelos.txt"):
    archivos_csv = glob.glob(os.path.join(carpeta_entrada, "*.csv"))
    if not archivos_csv:
        return

    print("\n" + "="*50)
    print("FASE 1")
    print("="*50)

    # 1. Recopilar todos los textos únicos para no traducir duplicados
    textos_unicos = {} # Formato: {hash: {'raw': texto, 'input': prompt}}
    
    for archivo in archivos_csv:
        try:
            df = pd.read_csv(archivo, engine='python', on_bad_lines='warn', encoding='utf-8')
            
            col_input = next((c for c in df.columns if ('input' in c.lower() or 'prompt' in c.lower() or 'origen' in c.lower()) and 'tipo' not in c.lower() and 'raw' not in c.lower()), None)
            col_raw = next((c for c in df.columns if 'raw' in c.lower() or 'original' in c.lower() or 'chino' in c.lower()), None)

            if col_input and col_raw:
                for _, row in df.iterrows():
                    t_raw = str(row[col_raw]).strip()
                    t_input = str(row[col_input]).strip()
                    
                    # Usamos el texto en chino como clave única
                    if t_raw not in textos_unicos and t_raw != 'nan':
                        textos_unicos[t_raw] = {'raw': t_raw, 'input': t_input}
        except Exception as e:
            continue

    if not textos_unicos:
        print("No se encontraron textos para traducir.")
        return

    # Preparamos el lote de traducción
    lote_datos = [{"id_temporal": i+1, "texto_raw": val['raw']} for i, val in enumerate(textos_unicos.values())]
    lote_json_str = json.dumps(lote_datos, ensure_ascii=False, indent=2)
    prompt_trad = crear_prompt_traduccion(lote_json_str)

    # Abrimos el archivo TXT para guardar en formato: modelo;texto_raw;texto_input;traduccion
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write("Modelo;Texto_Raw;Texto_Input;Traduccion_Raw\n")

        if USAR_GEMINI:
            print("  -> Pidiendo traducción a Gemini...")
            try:
                modelo = genai.GenerativeModel('gemini-2.5-flash-lite', generation_config={"response_mime_type": "application/json"})
                res = json.loads(modelo.generate_content(prompt_trad).text)
                for item in res.get('traducciones', []):
                    idx = item['id_temporal'] - 1
                    raw = lote_datos[idx]['texto_raw']
                    t_input = textos_unicos[raw]['input']
                    trad = item.get('traduccion_raw', '').replace('\n', ' ')
                    f.write(f"Gemini;{raw};{t_input};{trad}\n")
            except Exception as e: print(f"Error traduciendo con Gemini: {e}")

        if USAR_OPENAI:
            print("  -> Pidiendo traducción a OpenAI...")
            try:
                res = json.loads(cliente_openai.chat.completions.create(model="gpt-4o", response_format={"type": "json_object"}, messages=[{"role": "user", "content": prompt_trad}], temperature=0.0).choices[0].message.content)
                for item in res.get('traducciones', []):
                    idx = item['id_temporal'] - 1
                    raw = lote_datos[idx]['texto_raw']
                    t_input = textos_unicos[raw]['input']
                    trad = item.get('traduccion_raw', '').replace('\n', ' ')
                    f.write(f"OpenAI;{raw};{t_input};{trad}\n")
            except Exception as e: print(f"Error traduciendo con OpenAI: {e}")

        if USAR_CLAUDE:
            print("  -> Pidiendo traducción a Claude...")
            try:
                res = cliente_claude.messages.create(model="claude-haiku-4-5", max_tokens=4096, temperature=0.0, messages=[{"role": "user", "content": prompt_trad}])
                res_json = json.loads(res.content[0].text.replace("```json", "").replace("```", "").strip())
                for item in res_json.get('traducciones', []):
                    idx = item['id_temporal'] - 1
                    raw = lote_datos[idx]['texto_raw']
                    t_input = textos_unicos[raw]['input']
                    trad = item.get('traduccion_raw', '').replace('\n', ' ')
                    f.write(f"Claude;{raw};{t_input};{trad}\n")
            except Exception as e: print(f"Error traduciendo con Claude: {e}")

    print(f"Traducciones guardadas en: {archivo_salida}\n")

# FASE 2: PROMPTS Y FUNCIONES DE EVALUACIÓN
def crear_prompt_evaluacion(lote_json):
    return f"""
    Act as an expert computational linguist evaluating AI models.
    Below, you will receive a JSON-formatted list containing multiple inferences (input/output/raw text sets) to evaluate.
    
    DOMAIN CONTEXT:
    The text belongs to the "Wuxia" literary genre (and related genres like Xianxia/Xuanhuan). It features epic fantasy, Chinese martial arts, cultivation, sects, and language with a poetic, archaic, and honorific tone.

    STRICT RUBRIC FOR EACH INFERENCE:

    2. fidelidad (Scale 0 to 3 - Fidelity and Resolution):
        - Evaluate how well 'texto_output' resolves the task requested in 'texto_input' and preserves the meaning of the original 'texto_raw'.
        - 0 (Null/Refusal): The model collapses or the response is completely disconnected.
        - 1 (Inadequate): Severe false sense in the narrative. Translates the opposite, omits critical actions.
        - 2 (Partial): Solves the main task, but omits minor nuances of the action or context.
        - 3 (Complete): Perfect semantic transfer. Solves the task 100% preserving all information from the raw text.

    3. calidad (Scale 0 to 3 - Fluency and Cohesion):
        - Evaluate the linguistic quality of 'texto_output' in Spanish.
        - 0 (Unintelligible): Broken text or word salad.
        - 1 (Poor): Severe syntactic errors or literal structures.
        - 2 (Understandable): Correct grammar, but the narration sounds rigid, literal, or awkward.
        - 3 (Natural): Flawless. The text flows with the descriptive richness and naturalness of an expert writer.

    4. dominio (Scale 0 to 3 - Wuxia Terminology and Style):
        - Evaluate the use of genre-specific terminology and tone in 'texto_output'.
        - 0 (Contradictory): Uses modern, anachronistic jargon.
        - 1 (Generic/Baseline): Neutral response. Translates terms literally and generically.
        - 2 (Inconsistent): Mixes correct Wuxia terms with modern colloquialisms.
        - 3 (Precise): Flawless use of terminology (e.g., Qi, meridians, Jianghu, sects).

    5. alucinacion (Binary scale 0 or 1 - Narrative Factuality):
        - Evaluate if 'texto_output' invents elements not present in 'texto_raw'.
        - 0 (No hallucination / Success): The text strictly adheres to the events of the raw input.
        - 1 (Hallucination exists / Failure): The model introduces invented techniques, characters, or descriptions.

    INFERENCES TO EVALUATE:
    {lote_json}

    OUTPUT INSTRUCTION:
    Return ONLY a valid JSON object. This object must contain a "resultados" key 
    which is a list of objects, where each object corresponds to the evaluated "id_temporal".
    
    Exact expected format example:
    {{
      "resultados": [
        {{"id_temporal": 1, "fidelidad": 3, "calidad": 2, "dominio": 1, "alucinacion": 0}},
        {{"id_temporal": 2, "fidelidad": 2, "calidad": 3, "dominio": 3, "alucinacion": 1}}
      ]
    }}
    """

def ejecutar_evaluacion_lotes(carpeta_entrada="archivos_separados", carpeta_salida="archivos_evaluados"):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    archivos_csv = glob.glob(os.path.join(carpeta_entrada, "*.csv"))
    if not archivos_csv: return

    print("="*50)
    print("FASE 2")
    print("="*50)

    for archivo in archivos_csv:
        nombre_base = os.path.basename(archivo)
        print(f"\nEvaluando archivo: {nombre_base}...")
        
        try:
            df = pd.read_csv(archivo, engine='python', on_bad_lines='warn', encoding='utf-8')
        except: continue
        if df.empty: continue

        df['_id_temporal'] = range(1, len(df) + 1)
        
        col_input = next((c for c in df.columns if ('input' in c.lower() or 'prompt' in c.lower()) and 'tipo' not in c.lower() and 'raw' not in c.lower()), None)
        col_output = next((c for c in df.columns if 'output' in c.lower() or 'salida' in c.lower() or 'generado' in c.lower() or 'respuesta' in c.lower()), None)
        col_raw = next((c for c in df.columns if 'raw' in c.lower() or 'chino' in c.lower()), None)

        if not col_input or not col_output or not col_raw:
            print("  -> Faltan columnas, saltando.")
            continue

        lote_datos = [{"id_temporal": r['_id_temporal'], "texto_input": str(r[col_input]), "texto_raw": str(r[col_raw]), "texto_output": str(r[col_output])} for _, r in df.iterrows()]
        prompt_eval = crear_prompt_evaluacion(json.dumps(lote_datos, ensure_ascii=False, indent=2))

        # LLAMADAS APIS PARA EVALUAR
        mapa_gemini, mapa_openai, mapa_claude = {}, {}, {}
        
        if USAR_GEMINI:
            try:
                res = json.loads(genai.GenerativeModel('gemini-3-flash-preview', generation_config={"response_mime_type": "application/json"}).generate_content(prompt_eval).text)
                mapa_gemini = {i['id_temporal']: i for i in res.get('resultados', [])}
            except: pass

        if USAR_OPENAI:
            try:
                res = json.loads(cliente_openai.chat.completions.create(model="gpt-5.1-mini", response_format={"type": "json_object"}, messages=[{"role": "user", "content": prompt_eval}], temperature=0.0).choices[0].message.content)
                mapa_openai = {i['id_temporal']: i for i in res.get('resultados', [])}
            except: pass

        if USAR_CLAUDE:
            try:
                res = json.loads(cliente_claude.messages.create(model="claude-sonnet-4-6", max_tokens=4096, temperature=0.0, messages=[{"role": "user", "content": prompt_eval}]).content[0].text.replace("```json", "").replace("```", "").strip())
                mapa_claude = {i['id_temporal']: i for i in res.get('resultados', [])}
            except: pass

        # MAPEO AL DATAFRAME
        for index, row in df.iterrows():
            id_t = row['_id_temporal']
            if USAR_GEMINI and id_t in mapa_gemini:
                df.at[index, 'Gemini_Fidelidad'] = mapa_gemini[id_t].get('fidelidad')
                df.at[index, 'Gemini_Calidad'] = mapa_gemini[id_t].get('calidad')
                df.at[index, 'Gemini_Dominio'] = mapa_gemini[id_t].get('dominio')
                df.at[index, 'Gemini_Alucinacion'] = mapa_gemini[id_t].get('alucinacion')
            if USAR_OPENAI and id_t in mapa_openai:
                df.at[index, 'OpenAI_Fidelidad'] = mapa_openai[id_t].get('fidelidad')
                df.at[index, 'OpenAI_Calidad'] = mapa_openai[id_t].get('calidad')
                df.at[index, 'OpenAI_Dominio'] = mapa_openai[id_t].get('dominio')
                df.at[index, 'OpenAI_Alucinacion'] = mapa_openai[id_t].get('alucinacion')
            if USAR_CLAUDE and id_t in mapa_claude:
                df.at[index, 'Claude_Fidelidad'] = mapa_claude[id_t].get('fidelidad')
                df.at[index, 'Claude_Calidad'] = mapa_claude[id_t].get('calidad')
                df.at[index, 'Claude_Dominio'] = mapa_claude[id_t].get('dominio')
                df.at[index, 'Claude_Alucinacion'] = mapa_claude[id_t].get('alucinacion')

        df.drop(columns=['_id_temporal'], inplace=True)
        ruta_guardado = os.path.join(carpeta_salida, nombre_base)
        df.to_csv(ruta_guardado, index=False)
        print(f"  Guardado: {ruta_guardado}")
        time.sleep(3)

if __name__ == "__main__":
    if not USAR_GEMINI and not USAR_OPENAI and not USAR_CLAUDE:
        print("Advertencia: Todos los jueces están apagados (False).")
    else:
        ejecutar_traducciones_unicas()
        
        # ejecutar_evaluacion_lotes()
        
