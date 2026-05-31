import re
import os
import numpy as np
import pandas as pd
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from math import pi
import logging
from tqdm import tqdm
# Métricas clásicas
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import wordpunct_tokenize
import sacrebleu
from sacrebleu.metrics import CHRF, TER
from rouge_score import rouge_scorer

from bert_score import score as calc_bertscore
from comet import download_model, load_from_checkpoint

logging.getLogger("pytorch_lightning").setLevel(logging.WARNING)

# Lo cargamos aquí para que solo consuma RAM/VRAM una vez
print("Cargando modelo COMET (wmt22-comet-da)...")
comet_model_path = download_model("Unbabel/wmt22-comet-da")
comet_model = load_from_checkpoint(comet_model_path)
comet_model.eval()
print("Modelo COMET cargado correctamente.")

# Configuración para servidores sin monitor
plt.switch_backend('Agg')

# Configuración visual global
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

INPUT_DIR = Path("extra") 
OUTPUT_DIR = Path("evaluation")
OUTPUT_FILE_TXT = OUTPUT_DIR / "resultados_extra.txt"
OUTPUT_FILE_MD = OUTPUT_DIR / "resultados_extra.md"
OUTPUT_IMG_DIR = OUTPUT_DIR / "graficas_extra"

def extract_gen_content(text):
    match_triple = re.search(r"\[\[\[(.*?)\]\]\]", text, re.DOTALL)
    if match_triple: return match_triple.group(1).strip()
    match_double = re.search(r"\[\[(.*?)\]\]", text, re.DOTALL)
    if match_double: return match_double.group(1).strip()
    if "[[" in text:
        return text.replace("[[[", "").replace("]]]", "").replace("[[", "").replace("]]", "").strip()
    return text.strip()

def parse_test_file(filepath):
    content = filepath.read_text(encoding='utf-8')
    data = {}
    prompts_blocks = re.split(r"(### PROMPT \d+)", content)
    current_prompt = "Unknown"
    
    for section in prompts_blocks:
        if section.strip().startswith("### PROMPT"):
            current_prompt = section.strip().replace("### ", "")
            if current_prompt not in data: data[current_prompt] = {}
            continue
        if not section.strip(): continue

        shot_blocks = re.split(r"(=== \d+SHOT.*?===)", section)
        current_shot = "Unknown"
        for block in shot_blocks:
            if block.strip().startswith("===") and "SHOT" in block:
                match = re.search(r"(\d+SHOT)", block)
                if match:
                    current_shot = match.group(1)
                    if current_shot not in data[current_prompt]:
                        data[current_prompt][current_shot] = {'refs': [], 'preds': []}
                continue
            if not block.strip() or current_shot == "Unknown": continue

            cases = re.split(r"--- Case \d+ ---", block)
            for case in cases:
                if not case.strip(): continue
                ref_match = re.search(r"\[REF\]:\s*(.*?)(?=\n\[GEN\]|\[GEN\])", case, re.DOTALL)
                gen_match = re.search(r"\[GEN\]:\s*(.*)", case, re.DOTALL)
                if ref_match and gen_match:
                    raw_gen_text = gen_match.group(1).split("[TIME]")[0].strip()
                    data[current_prompt][current_shot]['refs'].append(ref_match.group(1).strip())
                    data[current_prompt][current_shot]['preds'].append(extract_gen_content(raw_gen_text))
    return data

def compute_metrics(preds, refs):
    # Si no hay predicciones, devolvemos todo a 0 (incluyendo las nuevas métricas)
    if not preds: 
        return {k: 0.0 for k in ["sacrebleu", "chrf2", "ter", "rougeL_f1", "meteor", "bertscore", "comet"]}
    
    # Métricas Clásicas
    bleu = sacrebleu.corpus_bleu(preds, [refs]).score
    chrf = CHRF(word_order=2).corpus_score(preds, [refs]).score
    ter = TER().corpus_score(preds, [refs]).score
    
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    rouge_avg = float(np.mean([scorer.score(r, h)['rougeL'].fmeasure for h, r in zip(preds, refs)])) * 100.0
    meteor_avg = float(np.mean([meteor_score([wordpunct_tokenize(r)], wordpunct_tokenize(h)) for h, r in zip(preds, refs)])) * 100.0
    
    _, _, F1 = calc_bertscore(preds, refs, lang="en", verbose=False)
    bertscore_avg = float(F1.mean()) * 100.0
    
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

def sort_shots(shot_list):
    return sorted(shot_list, key=lambda x: int(re.search(r'(\d+)', x).group(1)))

def get_shot_num(shot_str):
    return int(re.search(r'(\d+)', shot_str).group(1))

def generate_latex_md(df_all, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Reporte de Evaluación (Tablas LaTeX)\n\n")
        models = sorted(df_all['Model'].unique())
        for model in models:
            f.write(f"## Modelo: {model}\n\n")
            df_model = df_all[df_all['Model'] == model]
            prompts = sorted(df_model['Prompt'].unique())
            for prompt in prompts:
                f.write(f"### {prompt}\n\n")
                df_subset = df_model[df_model['Prompt'] == prompt]
                unique_shots = sort_shots(df_subset['Shot'].unique())
                pivot = df_subset.pivot(index="Metric", columns="Shot", values="Score")
                pivot = pivot.reindex(columns=unique_shots)
                latex = pivot.to_latex(float_format="%.2f", caption=f"{model} - {prompt}", label=f"tab:{model}_{prompt.replace(' ', '_')}", position="h")
                f.write(f"```latex\n{latex}```\n\n")


def plot_global_dashboard(df, output_dir):
    df_plot = df.copy()
    df_plot['Shot_Num'] = df_plot['Shot'].apply(get_shot_num)
    metrics = df_plot['Metric'].unique()
    cols = 3
    rows = (len(metrics) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(16, 5 * rows))
    axes = axes.flatten()
    for i, metric in enumerate(metrics):
        ax = axes[i]
        sns.lineplot(
            data=df_plot[df_plot['Metric'] == metric],
            x="Shot_Num", y="Score", hue="Model", style="Model",
            markers=True, dashes=False, linewidth=2,
            err_style="band", errorbar=("sd", 1), ax=ax
        )
        ax.set_title(f"Métrica: {metric.upper()}", fontsize=14, fontweight='bold')
        ax.set_xlabel("Shots (Contexto)")
        ax.set_ylabel("Score")
        ax.set_xticks(sorted(df_plot['Shot_Num'].unique()))
        if i == 0:
            ax.legend(title="Modelo", bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            if ax.get_legend(): ax.get_legend().remove()
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    plt.tight_layout()
    plt.savefig(output_dir / "0_dashboard_global.png", dpi=300)
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    files = sorted(list(INPUT_DIR.glob("*.txt")))
    if not files: 
        print("No hay archivos en final/")
        return

    with OUTPUT_FILE_TXT.open("w", encoding="utf-8") as f:
        f.write("REPORTE DE EVALUACIÓN\n\n")

    global_data = []
    
    metrics_list = ["sacrebleu", "chrf2", "ter", "rougeL_f1", "meteor", "bertscore", "comet"]

    print(f"\nIniciando evaluación de {len(files)} archivos...\n")

    for file_path in tqdm(files, desc="Procesando Modelos", position=0):
        model_name = file_path.stem 
        parsed = parse_test_file(file_path)
        
        all_prompts = sorted(list(parsed.keys()))
        if not all_prompts: continue
        
        raw_shots = {s for p in all_prompts for s in parsed[p].keys()}
        all_shots = sort_shots(list(raw_shots))
        
        txt_table_data = {}
        
        total_evals = len(all_prompts) * len(all_shots)
        with tqdm(total=total_evals, desc=f"Evaluando {model_name[:10]}...", position=1, leave=False) as pbar:
            
            for prompt in all_prompts:
                for shot in all_shots:
                    if shot in parsed[prompt]:
                        scores = compute_metrics(parsed[prompt][shot]['preds'], parsed[prompt][shot]['refs'])
                    else:
                        scores = {m: 0.0 for m in metrics_list}
                    
                    txt_table_data[(prompt, shot)] = [scores[m] for m in metrics_list]
                    for metric_name, score_value in scores.items():
                        global_data.append({
                            "Model": model_name, "Prompt": prompt, "Shot": shot,
                            "Metric": metric_name, "Score": score_value
                        })
                    
                    # Actualizar la barra secundaria
                    pbar.update(1)

        df_txt = pd.DataFrame(txt_table_data, index=metrics_list)
        df_txt.columns.names = ['PROMPT', 'SHOT']
        with OUTPUT_FILE_TXT.open("a", encoding="utf-8") as f:
            f.write(f"ARCHIVO: {file_path.name}\n")
            f.write(df_txt.to_string())
            f.write("\n\n" + "="*50 + "\n\n")

    if global_data:
        df_all = pd.DataFrame(global_data)
        
        df_all.to_csv(OUTPUT_DIR / "resultados_extra.csv", index=False)
        
        print("\nGenerando Markdown LaTeX y Gráficas...")
        generate_latex_md(df_all, OUTPUT_FILE_MD)
        
        graficas = [
            ("Dashboard Global", lambda: plot_global_dashboard(df_all, OUTPUT_IMG_DIR)),
            ("Scaling Laws", lambda: plot_scaling_laws(df_all, OUTPUT_IMG_DIR)),
            ("Boxplots", lambda: plot_boxplot(df_all, OUTPUT_IMG_DIR)),
            ("Heatmaps", lambda: plot_heatmap(df_all, OUTPUT_IMG_DIR)),
            ("Gráficos Radar", lambda: plot_radar(df_all, OUTPUT_IMG_DIR)),
            ("Barras Agrupadas", lambda: plot_grouped_bars(df_all, OUTPUT_IMG_DIR))
        ]
        
        for nombre, funcion_grafica in tqdm(graficas, desc="Creando Gráficas", position=0):
            funcion_grafica()
            
    print(f"\n¡Proceso completado con éxito! Revisa la carpeta: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()