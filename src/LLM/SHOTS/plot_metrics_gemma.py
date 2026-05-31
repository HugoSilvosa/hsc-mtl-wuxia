import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

INPUT_FILE = Path(r"C:\Users\Usuario\Desktop\TFG\CORPUS\src\LLM\evaluation\resultados_combinados.txt")
OUTPUT_DIR = Path(r"C:\Users\Usuario\Desktop\TFG\CORPUS\evaluation\fig\extra")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ORDER = ["gemma3_270m", "gemma3_1b", "gemma3_4b", "gemma3_12b", "gemma3_27b"]
SHOT_LABELS = ["0", "1", "2", "3", "5", "10"]

MODEL_PALETTE = {
    "gemma3_270m": "#c5b0d5",
    "gemma3_1b": "#98df8a",
    "gemma3_4b": "#1f77b4",
    "gemma3_12b": "#ff9896",
    "gemma3_27b": "#d62728"
}

def parse_all_shots(filepath):
    records = []
    current_model = None
    metricas_objetivo = ["sacrebleu", "meteor", "comet"]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError: return pd.DataFrame()

    for line in lines:
        line = line.strip()
        if line.startswith("ARCHIVO:"):
            current_model = line.split(":")[1].strip().replace(".txt", "")
            continue
        if not current_model or current_model == "hunyuan": continue
            
        parts = line.split()
        if len(parts) > 0 and parts[0] in metricas_objetivo:
            metric = parts[0]
            scores = parts[1:]
            for p_idx in range(5):
                for s_idx, shot_val in enumerate(SHOT_LABELS):
                    val_idx = (p_idx * 6) + s_idx
                    try:
                        records.append({
                            "Model": current_model,
                            "Metric": metric,
                            "Prompt": f"P{p_idx}",
                            "Shots": int(shot_val),
                            "Score": float(scores[val_idx]),
                            "Group": f"{current_model}_P{p_idx}"
                        })
                    except: continue
    return pd.DataFrame(records)

def plot_evolution(df):
    # 1. Configuración de Estilo y Fuentes (idéntico al dashboard)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    
    SIZE_TITLE = 28
    SIZE_LABEL = 26
    SIZE_TICKS = 23
    
    sns.set_theme(style="whitegrid")
    
    metrics = df['Metric'].unique()
    cols = 2
    rows = (len(metrics) + cols - 1) // cols
    
    # 2. Mismo figsize que el dashboard (proporción consistente)
    fig, axes = plt.subplots(rows, cols, figsize=(20, 7 * rows))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        df_m = df[df['Metric'] == metric]
        
        # Hilos individuales (alpha bajo)
        sns.lineplot(
            data=df_m, x="Shots", y="Score", hue="Model", units="Group",
            estimator=None, hue_order=MODEL_ORDER, palette=MODEL_PALETTE,
            linewidth=1.5, alpha=0.2, ax=ax, legend=False
        )
        
        # Promedios (línea gruesa)
        sns.lineplot(
            data=df_m, x="Shots", y="Score", hue="Model",
            estimator="mean", errorbar=None,
            hue_order=MODEL_ORDER, palette=MODEL_PALETTE,
            linewidth=4, marker="o", markersize=10, ax=ax
        )
        
        # Formato de ejes con tamaños consistentes
        ax.set_title(f"{metric.upper()}", fontsize=SIZE_TITLE, fontweight='bold', pad=20)
        ax.set_xlabel("Shots", fontsize=SIZE_LABEL, fontweight='bold')
        ax.set_ylabel("Score", fontsize=SIZE_LABEL, fontweight='bold')
        ax.tick_params(axis='both', which='major', labelsize=SIZE_TICKS)
        ax.set_xticks([0, 1, 2, 3, 5, 10])
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.get_legend().remove()
    # Eliminar subplots vacíos
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles, labels, 
        title="Modelos", 
        title_fontsize=30,
        fontsize=24,
        loc='center', 
        bbox_to_anchor=(0.75, 0.3), 
        frameon=True
    )
    
    # Ajustes finales para que coincida con la disposición del dashboard
    plt.tight_layout()
    fig.subplots_adjust(right=0.82) 
    
    output_path = OUTPUT_DIR / "evolucion_gemma.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    df = parse_all_shots(INPUT_FILE)
    if not df.empty:
        plot_evolution(df)

if __name__ == "__main__":
    main()