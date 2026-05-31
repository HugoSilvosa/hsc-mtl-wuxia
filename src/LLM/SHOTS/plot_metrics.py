import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from math import pi
import re
from tqdm import tqdm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
plt.switch_backend('Agg')

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

INPUT_CSV = Path(r"C:\Users\Usuario\Desktop\TFG\CORPUS\src\LLM\evaluation\resultados_globales.csv")
OUTPUT_IMG_DIR = Path(r"C:\Users\Usuario\Desktop\TFG\CORPUS\evaluation\fig\llm")

def sort_shots(shot_list):
    return sorted(shot_list, key=lambda x: int(re.search(r'(\d+)', str(x)).group(1)))

def get_shot_num(shot_str):
    return int(re.search(r'(\d+)', str(shot_str)).group(1))
import matplotlib.ticker as mticker

def plot_3d(df, output_dir):
    SIZE_TITLE = 25
    SIZE_LABEL = 23
    SIZE_TICKS = 18
    
    metrics = df['Metric'].unique()
    
    MODEL_PALETTE = {
        "Gemma_3": "#5294ea", "Gemma_3_QLoRA": "#1f77b4",
        "Llama_3": "#ed4643", "Llama_3_QLoRA": "#d62728",
        "GLM_4": "#63e54a", "GLM_4_QLoRA": "#2ca02c",
        "Qwen_3": "#c5b0d5", "Qwen_3_QLoRA": "#9467bd"
    }
    MODEL_MARKERS = {
        "Gemma_3": "o", "Gemma_3_QLoRA": "X",
        "Llama_3": "s", "Llama_3_QLoRA": "D",
        "GLM_4": "^", "GLM_4_QLoRA": "v",
        "Qwen_3": "p", "Qwen_3_QLoRA": "*"
    }

    modelos_base = ["Gemma_3", "Llama_3", "GLM_4", "Qwen_3"]
    df_base = df[df['Model'].isin(modelos_base)].copy()
    df_finetuned = df[df['Model'].str.contains('QLoRA', case=False)].copy()
    
    grupos = {'base': df_base, 'finetuned': df_finetuned}
    cols = 3
    rows = (len(metrics) + cols - 1) // cols
    
    for nombre_grupo, df_grupo in grupos.items():
        if df_grupo.empty: continue
            
        models_in_group = df_grupo['Model'].unique()
        fig = plt.figure(figsize=(24, 8 * rows)) 
        global_handles, global_labels = [], []
        
        for i, metric in enumerate(metrics):
            ax = fig.add_subplot(rows, cols, i + 1, projection='3d')
            df_metric = df_grupo[df_grupo['Metric'] == metric].copy()
            
            # Limpieza de índices
            df_metric['Prompt_Idx'] = df_metric['Prompt'].astype(str).str.extract(r'(\d+)')[0].astype(int)
            df_metric['Shot_Idx'] = df_metric['Shot'].astype(str).str.extract(r'(\d+)')[0].astype(int)
            
            for model in models_in_group:
                df_model = df_metric[df_metric['Model'] == model].copy()
                c, m = MODEL_PALETTE.get(model, "gray"), MODEL_MARKERS.get(model, "o")
                
                scatter = ax.scatter(df_model['Prompt_Idx'], df_model['Shot_Idx'], df_model['Score'], 
                                color=c, marker=m, s=120, alpha=0.9, edgecolors='w')
                
                if i == 0:
                    global_handles.append(scatter)
                    global_labels.append(model)
                
                for p_val in df_model['Prompt_Idx'].unique():
                    df_line = df_model[df_model['Prompt_Idx'] == p_val].sort_values('Shot_Idx')
                    ax.plot(df_line['Prompt_Idx'], df_line['Shot_Idx'], df_line['Score'], color=c, alpha=0.3, linewidth=2)

            ax.set_title(f"{metric.upper()}", fontsize=SIZE_TITLE, fontweight='bold', pad=30)
            
            ax.set_xlabel("Prompt", fontsize=SIZE_LABEL, labelpad=15, fontweight='bold')
            ax.set_ylabel("Shots", fontsize=SIZE_LABEL, labelpad=15, fontweight='bold')
            ax.set_zlabel("Score", fontsize=SIZE_LABEL, labelpad=15, fontweight='bold')
            
            # Forzamos que los ticks de X e Y sean enteros
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            
            # Agranda los números (ticks)
            ax.tick_params(axis='both', which='major', labelsize=SIZE_TICKS, pad=8)
            
            # Ajuste de perspectiva
            ax.dist = 11.5 
            ax.view_init(elev=20, azim=-45)

        # Leyenda 
        fig.legend(global_handles, global_labels, title="Modelos", title_fontsize=SIZE_LABEL,
                loc='upper right', bbox_to_anchor=(0.85, 0.5), fontsize=SIZE_LABEL)
        
        fig.subplots_adjust(left=0.02, right=0.88, top=0.90, wspace=0.35, hspace=0.3)
        plt.savefig(output_dir / f"6_3d_dashboard_{nombre_grupo}.png", dpi=300, bbox_inches='tight')
        plt.close()


MODEL_PALETTE = {
    "Gemma_3": "#aec7e8",     
    "Gemma_3_QLoRA": "#1f77b4", 
    "Llama_3": "#ff9896",     
    "Llama_3_QLoRA": "#d62728", 
    "GLM_4": "#98df8a",        
    "GLM_4_QLoRA": "#2ca02c",   
    "Qwen_3": "#c5b0d5",      
    "Qwen_3_QLoRA": "#9467bd"   
}

# Marcadores distintos para base vs finetuned
MODEL_MARKERS = {
    "Gemma_3": "o", "gemma3_finetuned": "X",
    "Llama_3": "s", "llama3_finetuned": "D",
    "GLM_4": "^", "glm_finetuned": "v",
    "Qwen_3": "p", "Qwen_3_finetuned": "*",
    "Gemma_3_QLoRA": "o", 
    "Llama_3_QLoRA": "s", 
    "GLM_4_QLoRA": "^", 
    "Qwen_3_QLoRA": "p"
}


def plot_prompts_dashboard(df, output_dir):
    SIZE_TITLE = 28
    SIZE_LABEL = 26
    SIZE_TICKS = 23
    
    
    df_plot = df.copy()
    
    prompt_order = ["BASE", "FANT", "LIT", "MT", "ACAD"]

    prompt_map = {"0": "BASE", "1": "FANT", "2": "LIT", "3": "MT", "4": "ACAD"}
    df_plot['Prompt'] = df_plot['Prompt'].astype(str).map(prompt_map)
    df_plot['Prompt'] = pd.Categorical(df_plot['Prompt'], categories=prompt_order, ordered=True)
    
    metrics = df_plot['Metric'].unique()
    
    
    cols = 3
    rows = (len(metrics) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(20, 7 * rows)) 
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        sns.lineplot(
                data=df_plot[df_plot['Metric'] == metric],
                x="Prompt", y="Score", 
                hue="Model", style="Model",
                palette=MODEL_PALETTE,  
                markers=MODEL_MARKERS,  
                dashes=False, linewidth=2.5,
                markersize=10,
                errorbar=None, ax=ax
        )
        
        ax.set_title(f"{metric.upper()}", fontsize=SIZE_TITLE, fontweight='bold', pad=15)
        ax.set_xlabel("Prompt", fontsize=SIZE_LABEL, fontweight='bold')
        ax.set_ylabel("Score", fontsize=SIZE_LABEL, fontweight='bold')
        
        # Ticks más grandes
        ax.tick_params(axis='both', which='major', labelsize=SIZE_TICKS)
        
        if ax.get_legend():
            ax.get_legend().remove()

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles, labels, 
        title="Modelos", title_fontsize=SIZE_LABEL,
        loc='center left', 
        bbox_to_anchor=(0.75, 0.35), 
        ncol=1,                     
        frameon=True,
        fontsize=SIZE_TICKS
    )

    plt.tight_layout()
    fig.subplots_adjust(right=0.85, bottom=0.15) 
    
    plt.savefig(output_dir / "0_dashboard_prompts.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    
def plot_global_dashboard(df, output_dir):
    SIZE_TITLE = 28
    SIZE_LABEL = 26
    SIZE_TICKS = 23

    df_plot = df.copy()
    df_plot['Shot_Num'] = df_plot['Shot'].apply(get_shot_num)
    metrics = df_plot['Metric'].unique()
    
    cols = 3
    rows = (len(metrics) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(18, 6 * rows))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        sns.lineplot(
            data=df_plot[df_plot['Metric'] == metric],
            x="Shot_Num", y="Score", 
            hue="Model", style="Model",
            palette=MODEL_PALETTE,  
            markers=MODEL_MARKERS,  
            dashes=False, linewidth=2.5, 
            markersize=10,               
            errorbar=None, ax=ax
        )
        
        # Títulos y etiquetas 
        ax.set_title(f"{metric.upper()}", fontsize=SIZE_TITLE, fontweight='bold', pad=15)
        ax.set_xlabel("Shots", fontsize=SIZE_LABEL, fontweight='bold')
        ax.set_ylabel("Score", fontsize=SIZE_LABEL, fontweight='bold')
        
        # Ticks 
        ax.tick_params(axis='both', which='major', labelsize=SIZE_TICKS)
        
        if ax.get_legend():
            ax.get_legend().remove()

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    handles, labels = ax.get_legend_handles_labels()
    
    fig.legend(
        handles, labels, 
        title="Modelos", title_fontsize=SIZE_LABEL,
        loc='center left', 
        bbox_to_anchor=(0.75, 0.30), 
        ncol=1,                     
        frameon=True,
        fontsize=SIZE_TICKS
    )

    plt.tight_layout()
    fig.subplots_adjust(right=0.85, bottom=0.12) 
    
    plt.savefig(output_dir / "0_dashboard_shots.png", dpi=300, bbox_inches='tight')
    plt.close()
    
def plot_scaling_laws(df, output_dir):
    df_plot = df.copy()
    df_plot['Shot_Num'] = df_plot['Shot'].apply(get_shot_num)
    metrics = df_plot['Metric'].unique()
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        sns.lineplot(
            data=df_plot[df_plot['Metric'] == metric],
            x="Shot_Num", y="Score", hue="Model", style="Model",
            markers=True, dashes=False, linewidth=2.5,
            err_style="band", errorbar=("sd", 1)
        )
        plt.title(f"Tendencia: {metric} vs Contexto (Scaling)")
        plt.xlabel("Número de Shots")
        plt.ylabel(f"Score {metric}")
        plt.xticks(sorted(df_plot['Shot_Num'].unique()))
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(output_dir / f"1_scaling_{metric}.png", dpi=300)
        plt.close()

def plot_boxplot(df, output_dir):
    df_plot = df.copy()
    unique_shots = sort_shots(df_plot['Shot'].unique())
    metrics = df_plot['Metric'].unique()
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=df_plot[df_plot['Metric'] == metric],
            x="Shot", y="Score", hue="Model",
            order=unique_shots, palette="Set2"
        )
        plt.title(f"Estabilidad y Varianza: {metric}")
        plt.xlabel("Shot")
        plt.ylabel("Score")
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(output_dir / f"2_boxplot_{metric}.png", dpi=300)
        plt.close()

def plot_heatmap(df, output_dir):
    target_metrics = ["sacrebleu", "rougeL_f1", "bertscore", "comet"]
    models = df['Model'].unique()
    unique_shots = sort_shots(df['Shot'].unique())
    for model in models:
        for metric in target_metrics:
            df_sub = df[(df['Model'] == model) & (df['Metric'] == metric)]
            if df_sub.empty: continue
            pivot = df_sub.pivot(index="Prompt", columns="Shot", values="Score")
            pivot = pivot.reindex(columns=unique_shots)
            plt.figure(figsize=(8, len(pivot)*0.8 + 2))
            sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt=".1f", cbar_kws={'label': 'Score'})
            plt.title(f"Heatmap: {model} - {metric}")
            plt.tight_layout()
            plt.savefig(output_dir / f"3_heatmap_{model}_{metric}.png", dpi=300)
            plt.close()

def plot_radar(df, output_dir):
    shots = df['Shot'].unique()
    for shot in shots:
        df_shot = df[df['Shot'] == shot].groupby(['Model', 'Metric'])['Score'].mean().reset_index()
        metrics = df_shot['Metric'].unique().tolist()
        models = df_shot['Model'].unique().tolist()
        if not metrics: continue
        num_vars = len(metrics)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)
        plt.xticks(angles[:-1], metrics, color='grey', size=10)
        palette = sns.color_palette("bright", len(models))
        for idx, model in enumerate(models):
            values = []
            for m in metrics:
                val = df_shot[(df_shot['Model'] == model) & (df_shot['Metric'] == m)]['Score'].values
                values.append(val[0] if len(val) > 0 else 0)
            values += values[:1]
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=model, color=palette[idx])
            ax.fill(angles, values, color=palette[idx], alpha=0.1)
        plt.title(f"Perfil de Modelos ({shot})", size=15, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.savefig(output_dir / f"4_radar_{shot}.png", dpi=300)
        plt.close()

def plot_grouped_bars(df, output_dir):
    unique_shots = sort_shots(df['Shot'].unique())
    metrics = df['Metric'].unique()
    for metric in metrics:
        plt.figure(figsize=(12, 6))
        sns.barplot(
            data=df[df['Metric'] == metric],
            x="Shot", y="Score", hue="Model",
            order=unique_shots, palette="muted",
            errorbar="sd", capsize=.1 
        )
        plt.title(f"Comparativa Directa: {metric}")
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(output_dir / f"5_bars_{metric}.png", dpi=300)
        plt.close()

def main():
    if not INPUT_CSV.exists():
        print(f"Error: No se encontró el archivo {INPUT_CSV}.")
        print("Asegúrate de exportar df_all.to_csv() en tu script principal primero.")
        return

    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Cargando datos desde {INPUT_CSV}...")
    df_all = pd.read_csv(INPUT_CSV)
    metricas_deseadas = ["sacrebleu", "chrf2", "rougeL_f1", "meteor", "comet"]
    df_all = df_all[df_all['Metric'].isin(metricas_deseadas)]
    if df_all.empty:
        print("El CSV está vacío. Revisa la ejecución original.")
        return

    graficas = [
        ("Dashboard Shots", lambda: plot_global_dashboard(df_all, OUTPUT_IMG_DIR)),
        ("Gráficos 3D", lambda: plot_3d(df_all, OUTPUT_IMG_DIR)),
        ("Dashboard Prompts", lambda: plot_prompts_dashboard(df_all, OUTPUT_IMG_DIR)),
        ("Scaling Laws", lambda: plot_scaling_laws(df_all, OUTPUT_IMG_DIR)),
        ("Boxplots", lambda: plot_boxplot(df_all, OUTPUT_IMG_DIR)),
        ("Heatmaps", lambda: plot_heatmap(df_all, OUTPUT_IMG_DIR)),
        ("Gráficos Radar", lambda: plot_radar(df_all, OUTPUT_IMG_DIR)),
        ("Barras Agrupadas", lambda: plot_grouped_bars(df_all, OUTPUT_IMG_DIR))
    ]
    
    for nombre, funcion_grafica in tqdm(graficas, desc="Generando Gráficas", position=0):
        funcion_grafica()
        
    print(f"\n¡Gráficas generadas exitosamente en: {OUTPUT_IMG_DIR}!")

if __name__ == "__main__":
    main()