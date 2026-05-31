import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.switch_backend('Agg')
sns.set_theme(style="whitegrid", context="paper", font_scale=1.6)

INPUT_DIR = Path("final")
OUTPUT_DIR = Path("evaluation")
OUTPUT_FILE_TIMES = OUTPUT_DIR / "tiempos_inferencia.txt"
OUTPUT_IMG_DIR = OUTPUT_DIR / "graficas"

# Diccionarios de mapeo, color y orden
NAME_MAPPING = {
    "gemma3_base": "Gemma_3", "gemma3_finetuned": "Gemma_3_QLoRA",
    "llama3_base": "Llama_3", "llama3_finetuned": "Llama_3_QLoRA",
    "glm_base": "GLM_4", "glm_finetuned": "GLM_4_QLoRA",
    "qwen3_base": "Qwen_3", "qwen3_finetuned": "Qwen_3_QLoRA"
}

MODEL_PALETTE = {
    "Gemma_3": "#5294ea", "Gemma_3_QLoRA": "#1f77b4",
    "Llama_3": "#ed4643", "Llama_3_QLoRA": "#d62728",
    "GLM_4": "#63e54a", "GLM_4_QLoRA": "#2ca02c",
    "Qwen_3": "#c5b0d5", "Qwen_3_QLoRA": "#9467bd"
}

# Ordenpara las barras y las leyendas
MODEL_ORDER = [
    "Gemma_3", "Gemma_3_QLoRA",
    "GLM_4", "GLM_4_QLoRA",
    "Llama_3", "Llama_3_QLoRA",
    "Qwen_3", "Qwen_3_QLoRA"
]

def process_times():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    files = sorted(list(INPUT_DIR.glob("*.txt")))
    
    data_llm = []
    
    # Expresiones regulares
    prompt_pattern = re.compile(r"(?i)TOTAL PROMPT\s*(\d+):\s*([\d.]+)\s*min")
    shot_pattern = re.compile(r"(?i)Mean Time\s*(\d+)\s*[-_]?shot.*?Total.*?:\s*([\d.]+)")
    
    # Procesar LLMs
    for file_path in files:
        raw_model_name = file_path.stem
        model_name = NAME_MAPPING.get(raw_model_name, raw_model_name)
        
        content = file_path.read_text(encoding='utf-8')
        
        for prompt_num, time_val in prompt_pattern.findall(content):
            data_llm.append({
                "Model": model_name,
                "Type": f"Prompt {prompt_num}",
                "Category": "Prompt",
                "Sort_Key": int(prompt_num),
                "Time (min)": float(time_val)
            })
            
        for shot_num, total_sec in shot_pattern.findall(content):
            data_llm.append({
                "Model": model_name,
                "Type": f"{shot_num}-Shot",
                "Category": "Shot",
                "Sort_Key": int(shot_num),
                "Time (min)": float(total_sec) / 60.0
            })

    if not data_llm:
        print("No se encontraron datos para procesar.")
        return

    df_llm = pd.DataFrame(data_llm)
    
    with OUTPUT_FILE_TIMES.open("w", encoding="utf-8") as f:
        f.write("=== REPORTE DE TIEMPOS DE INFERENCIA (MINUTOS) ===\n")
        f.write("Nota: Tiempos de Shots convertidos de segundos a minutos.\n")
        f.write("Nota 2: Si había registros duplicados, se ha calculado la media.\n\n")
        
        pivot_llm = df_llm.pivot_table(index="Model", columns="Type", values="Time (min)", aggfunc="mean")
        f.write("=== TABLA DE TIEMPOS - LLMs (Prompts & Shots) ===\n")
        f.write(pivot_llm.to_string(na_rep="-"))
        f.write("\n\n")
        
    df_shots = df_llm[df_llm["Category"] == "Shot"].sort_values("Sort_Key")
    df_prompts = df_llm[df_llm["Category"] == "Prompt"].sort_values("Sort_Key")
    
    unique_models = df_llm["Model"].unique()
    line_styles = {m: "" if "QLoRA" in m else (4, 2) for m in unique_models}

    # --- Gráfica 1: SHOTS (Evolución en Líneas) ---
    if not df_shots.empty:
        plt.figure(figsize=(14, 7))
        sns.lineplot(
            data=df_shots, 
            x="Type", 
            y="Time (min)", 
            hue="Model", 
            style="Model", 
            palette=MODEL_PALETTE,
            dashes=line_styles,
            markers=True,
            linewidth=3.5,            
            markersize=12,            
            errorbar=None, 
            hue_order=MODEL_ORDER, 
            style_order=MODEL_ORDER
        )
        
        plt.ylabel("Tiempo Total (Minutos)", fontsize=18, labelpad=15)
        plt.xlabel("Contexto (Shots)", fontsize=18, labelpad=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        
        # Leyenda más grande
        plt.legend(title="Modelo", bbox_to_anchor=(1.02, 1), loc='upper left', 
                fontsize=15, title_fontsize=17, markerscale=1.5)
        
        plt.tight_layout()
        # bbox_inches='tight' evita que la leyenda se recorte al guardarse
        plt.savefig(OUTPUT_IMG_DIR / "6a_tiempos_shots.png", dpi=300, bbox_inches='tight')
        plt.close()

    # --- Gráfica 2: PROMPTS (Barras Agrupadas) ---
    if not df_prompts.empty:
        plt.figure(figsize=(16, 8))
        sns.barplot(
            data=df_prompts, 
            x="Type", 
            y="Time (min)", 
            hue="Model", 
            palette=MODEL_PALETTE,
            hue_order=MODEL_ORDER,
            errorbar=None
        )
        
        # Textos más grandes
        # plt.title("Tiempos de Inferencia: Prompts", fontsize=22, fontweight='bold', pad=20)
        plt.ylabel("Tiempo Total (Minutos)", fontsize=18, labelpad=15)
        plt.xlabel("Prompt Evaluado", fontsize=18, labelpad=15)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        
        # Leyenda más grande
        plt.legend(title="Modelo", bbox_to_anchor=(1.02, 1), loc='upper left', 
                    fontsize=15, title_fontsize=17)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_IMG_DIR / "6b_tiempos_prompts.png", dpi=300, bbox_inches='tight')
        plt.close()

    print("\nProceso completado con éxito:")
    print(f"- Registros procesados: {len(data_llm)}")
    print(f"- Tablas guardadas en: {OUTPUT_FILE_TIMES}")
    print(f"- Gráficas guardadas en: {OUTPUT_IMG_DIR} (6a_tiempos_shots.png y 6b_tiempos_prompts.png)")

if __name__ == "__main__":
    process_times()