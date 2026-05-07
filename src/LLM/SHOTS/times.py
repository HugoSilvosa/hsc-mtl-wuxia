import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración visual
plt.switch_backend('Agg')
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# Configuración de rutas
INPUT_DIR = Path("final")
NMT_FILE = Path("evaluation/nmt.txt") 
OUTPUT_DIR = Path("evaluation")
OUTPUT_FILE_TIMES = OUTPUT_DIR / "tiempos_inferencia.txt"
OUTPUT_IMG_DIR = OUTPUT_DIR / "graficas"

def load_nmt_data():
    """Lee el archivo nmt.txt usando Regex para extraer los tiempos."""
    nmt_results = []
    
    if not NMT_FILE.exists():
        print(f"Advertencia: No se encontró el archivo NMT en {NMT_FILE.absolute()}")
        return nmt_results

    try:
        content = NMT_FILE.read_text(encoding='utf-8')
        blocks = content.split('{')
        for block in blocks:
            if not block.strip(): continue
                
            model_match = re.search(r'"model"\s*:\s*"([^"]+)"', block)
            stage_match = re.search(r'"stage"\s*:\s*"([^"]+)"', block)
            n_eval_match = re.search(r'"n_eval"\s*:\s*(\d+)', block)
            time_match = re.search(r'"execution_time"\s*:\s*([\d.]+)', block)
            
            if n_eval_match and int(n_eval_match.group(1)) == 1000:
                if model_match and time_match:
                    model_name = model_match.group(1)
                    if stage_match:
                        stage = stage_match.group(1)
                        if '/' not in model_name and stage not in model_name:
                            model_name = f"{model_name}_{stage}"

                    nmt_results.append({
                        "Model": model_name,
                        "Type": "NMT Eval (1k)",
                        "Time (min)": float(time_match.group(1)) / 60.0
                    })
    except Exception as e:
        print(f"Error procesando {NMT_FILE}: {e}")
    
    return nmt_results

def process_times():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    files = sorted(list(INPUT_DIR.glob("*.txt")))
    
    data_llm = []
    
    # --- EXPRESIONES REGULARES ACTUALIZADAS ---
    prompt_pattern = re.compile(r"(?i)TOTAL PROMPT\s*(\d+):\s*([\d.]+)\s*min")
    
    # Esta nueva versión acepta "Total Process Time:", "Total Time:", o "Total:"
    shot_pattern = re.compile(r"(?i)Mean Time\s*(\d+)\s*[-_]?shot.*?Total.*?:\s*([\d.]+)")
    # ------------------------------------------
    
    # 1. Procesar LLMs (archivos en final/)
    for file_path in files:
        model_name = file_path.stem
        content = file_path.read_text(encoding='utf-8')
        
        for prompt_num, time_val in prompt_pattern.findall(content):
            data_llm.append({
                "Model": model_name,
                "Type": f"Prompt {prompt_num}",
                "Time (min)": float(time_val)
            })
            
        for shot_num, total_sec in shot_pattern.findall(content):
            data_llm.append({
                "Model": model_name,
                "Type": f"{shot_num}-Shot",
                "Time (min)": float(total_sec) / 60.0 # Pasamos de segundos a minutos
            })

    # 2. Procesar NMTs
    data_nmt = load_nmt_data()
    
    # Convertir a DataFrames
    df_llm = pd.DataFrame(data_llm) if data_llm else pd.DataFrame()
    df_nmt = pd.DataFrame(data_nmt) if data_nmt else pd.DataFrame()
    
    # 3. Guardar Tablas SEPARADAS en el TXT
    with OUTPUT_FILE_TIMES.open("w", encoding="utf-8") as f:
        f.write("=== REPORTE DE TIEMPOS DE INFERENCIA (MINUTOS) ===\n")
        f.write("Nota: Tiempos de Shots y NMT convertidos de segundos a minutos.\n")
        f.write("Nota 2: Si había registros duplicados, se ha calculado la media.\n\n")
        
        if not df_llm.empty:
            pivot_llm = df_llm.pivot_table(index="Model", columns="Type", values="Time (min)", aggfunc="mean")
            f.write("=== TABLA DE TIEMPOS - LLMs (Prompts & Shots) ===\n")
            f.write(pivot_llm.to_string(na_rep="-"))
            f.write("\n\n")
            
            # Gráfica LLMs
            plt.figure(figsize=(14, 7))
            sns.barplot(data=df_llm, x="Type", y="Time (min)", hue="Model", palette="viridis", 
                        order=sorted(df_llm['Type'].unique()))
            plt.title("Tiempos de Inferencia: LLMs (Prompts y Shots)", fontsize=14, fontweight='bold')
            plt.ylabel("Tiempo Total (Minutos)")
            plt.xlabel("Etapa de Evaluación")
            plt.xticks(rotation=45)
            plt.legend(title="Modelo LLM", bbox_to_anchor=(1.02, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(OUTPUT_IMG_DIR / "6a_tiempos_llm.png", dpi=300)
            plt.close()
            
        if not df_nmt.empty:
            pivot_nmt = df_nmt.pivot_table(index="Model", columns="Type", values="Time (min)", aggfunc="mean")
            f.write("=== TABLA DE TIEMPOS - MODELOS NMT ===\n")
            f.write(pivot_nmt.to_string(na_rep="-"))
            f.write("\n\n================================================\n")
            
            # Gráfica NMTs
            plt.figure(figsize=(8, 6))
            sns.barplot(data=df_nmt, x="Model", y="Time (min)", hue="Model", palette="magma")
            plt.title("Tiempos de Inferencia: NMTs (n_eval=1000)", fontsize=14, fontweight='bold')
            plt.ylabel("Tiempo Total (Minutos)")
            plt.xlabel("Modelo NMT")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(OUTPUT_IMG_DIR / "6b_tiempos_nmt.png", dpi=300)
            plt.close()

    print("\nProceso completado con éxito:")
    print(f"- Registros LLM encontrados: {len(data_llm)}")
    print(f"- Registros NMT encontrados: {len(data_nmt)}")
    print(f"- Tablas separadas guardadas en: {OUTPUT_FILE_TIMES}")
    print(f"- Gráficas guardadas en: {OUTPUT_IMG_DIR} (6a_tiempos_llm.png y 6b_tiempos_nmt.png)")

if __name__ == "__main__":
    process_times()