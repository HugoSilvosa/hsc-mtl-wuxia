import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS ---
INPUT_FILE = Path("evaluation/resultados_combinados.txt")
OUTPUT_DIR = Path("evaluation/gemma/evolucion")
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

def plot_evolution_max_legibility(df):
    # Configuración de estilo de alto contraste y tamaño grande
    sns.set_theme(style="whitegrid", rc={
        "font.size": 16,
        "axes.titlesize": 22,
        "axes.labelsize": 18,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "legend.fontsize": 16,
        "legend.title_fontsize": 18
    })
    
    metrics = df['Metric'].unique()
    cols = 2
    rows = (len(metrics) + cols - 1) // cols
    
    # Aumentamos el tamaño de la figura (Ancho x Alto)
    fig, axes = plt.subplots(rows, cols, figsize=(22, 8 * rows))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        df_m = df[df['Metric'] == metric]
        
        # 1. Hilos de prompts (Finos)
        sns.lineplot(
            data=df_m, x="Shots", y="Score", hue="Model", units="Group",
            estimator=None, hue_order=MODEL_ORDER, palette=MODEL_PALETTE,
            linewidth=1.2, alpha=0.25, ax=ax, legend=False
        )
        
        # 2. Promedio (Muy grueso y visible)
        sns.lineplot(
            data=df_m, x="Shots", y="Score", hue="Model",
            estimator="mean", errorbar=None,
            hue_order=MODEL_ORDER, palette=MODEL_PALETTE,
            linewidth=5, marker="o", markersize=12, ax=ax
        )
        
        ax.set_title(f"Métrica: {metric.upper()}", fontweight='bold', pad=20)
        ax.set_xlabel("Shots", fontweight='bold', labelpad=15)
        ax.set_ylabel("Score", fontweight='bold', labelpad=15)
        ax.set_xticks([0, 1, 2, 3, 5, 10])
        
        # Añadir un grid más visible
        ax.grid(True, linestyle='--', alpha=0.7)

        # Manejo de la leyenda
        if i == 1: # Colocar la leyenda solo en el primer gráfico de la derecha
            ax.legend(title="Modelos (Promedio)", bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
        elif i != 1:
            if ax.get_legend(): ax.get_legend().remove()

    # Eliminar espacios vacíos si el número de métricas es impar
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout(rect=[0, 0, 0.9, 1]) # Ajustar para dejar espacio a la leyenda
    
    output_path = OUTPUT_DIR / "evolucion_gemma.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    df = parse_all_shots(INPUT_FILE)
    if not df.empty:
        plot_evolution_max_legibility(df)

if __name__ == "__main__":
    main()