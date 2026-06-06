import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from tqdm import tqdm

INPUT_DIR = Path(r"final") 
OUTPUT_DIR = Path(r"C:\Users\Usuario\Desktop\TFG\CORPUS\evaluation\LLM")
OUTPUT_FIG_DIR = Path(r"C:\Users\Usuario\Desktop\TFG\CORPUS\evaluation\fig")

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

MODEL_PALETTE = {
    "gemma3_base": "#aec7e8",     
    "gemma3_finetuned": "#1f77b4", 
    "llama3_base": "#ff9896",     
    "llama3_finetuned": "#d62728", 
    "glm_base": "#98df8a",        
    "glm_finetuned": "#2ca02c",   
    "qwen3_base": "#c5b0d5",      
    "qwen3_finetuned": "#9467bd"   
}

MODEL_MARKERS = {
    "gemma3_base": "o", "gemma3_finetuned": "X",
    "llama3_base": "s", "llama3_finetuned": "D",
    "glm_base": "^", "glm_finetuned": "v",
    "qwen3_base": "p", "qwen3_finetuned": "*"
}

def extract_gen_content(text):
    match_triple = re.search(r"\[\[\[(.*?)\]\]\]", text, re.DOTALL)
    if match_triple: return match_triple.group(1).strip()
    match_double = re.search(r"\[\[(.*?)\]\]", text, re.DOTALL)
    if match_double: return match_double.group(1).strip()
    if "[[" in text:
        return text.replace("[[[", "").replace("]]]", "").replace("[[", "").replace("]]", "").strip()
    return text.strip()

def sort_shots(shot_list):
    return sorted(shot_list, key=lambda x: int(re.search(r'(\d+)', x).group(1)))

def get_shot_num(shot_str):
    match = re.search(r'(\d+)', str(shot_str))
    return int(match.group(1)) if match else 0

def plot_length_evolution(df, output_dir):
    SIZE_TITLE = 28
    SIZE_LABEL = 26
    SIZE_TICKS = 23

    df_plot = df.copy()
    df_plot['Shot_Num'] = df_plot['Shot'].apply(get_shot_num)
    
    df_grouped = df_plot.groupby(['Model', 'Shot_Num'])['Word_Length'].mean().reset_index()

    plt.figure(figsize=(14, 8))
    
    ax = sns.lineplot(
        data=df_grouped,
        x="Shot_Num", y="Word_Length", 
        hue="Model", style="Model",
        palette=MODEL_PALETTE,  
        markers=MODEL_MARKERS,  
        dashes=False, linewidth=3.0, 
        markersize=12
    )
    
    ax.set_title("Evolución de la verbosidad en los shots (Media de palabras)", fontsize=SIZE_TITLE, fontweight='bold', pad=15)
    ax.set_xlabel("Contexto (Shots)", fontsize=SIZE_LABEL, fontweight='bold')
    ax.set_ylabel("Longitud Generada (Palabras)", fontsize=SIZE_LABEL, fontweight='bold')
    
    unique_shots = sorted(df_grouped['Shot_Num'].unique())
    ax.set_xticks(unique_shots)
    ax.set_xticklabels([f"{s}-Shot" for s in unique_shots])
    
    ax.tick_params(axis='both', which='major', labelsize=SIZE_TICKS)
    
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(
        handles, labels, 
        title="Modelos", title_fontsize=SIZE_LABEL,
        loc='center left', 
        bbox_to_anchor=(1.02, 0.5), 
        ncol=1,                     
        frameon=True,
        fontsize=SIZE_TICKS
    )

    plt.tight_layout()
    plt.savefig(output_dir / "evolucion_longitud_shots.png", dpi=300, bbox_inches='tight')
    plt.close()

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    files = sorted(list(INPUT_DIR.glob("*.txt")))
    if not files: 
        return
    
    data_rows = []

    for file_path in tqdm(files, desc="Procesando modelos", position=0):
        model_name = file_path.stem 
        content = file_path.read_text(encoding='utf-8')
        
        prompts_blocks = re.split(r"(### PROMPT \d+)", content)
        current_prompt = "Unknown"
        
        for section in prompts_blocks:
            if section.strip().startswith("### PROMPT"):
                current_prompt = section.strip().replace("### ", "")
                continue
            if not section.strip(): continue

            shot_blocks = re.split(r"(=== \d+SHOT.*?===)", section)
            current_shot = "Unknown"
            
            for block in shot_blocks:
                if block.strip().startswith("===") and "SHOT" in block:
                    match = re.search(r"(\d+SHOT)", block)
                    if match:
                        current_shot = match.group(1)
                    continue
                if not block.strip() or current_shot == "Unknown": continue

                cases = re.split(r"--- Case \d+ ---", block)
                for case in cases:
                    if not case.strip(): continue
                    
                    gen_match = re.search(r"\[GEN\]:\s*(.*)", case, re.DOTALL)
                    if gen_match:
                        raw_gen_text = gen_match.group(1).split("[TIME]")[0].strip()
                        clean_gen_text = extract_gen_content(raw_gen_text)
                        
                        char_length = len(clean_gen_text)
                        word_length = len(clean_gen_text.split())
                        
                        data_rows.append({
                            "Model": model_name,
                            "Prompt": current_prompt,
                            "Shot": current_shot,
                            "Char_Length": char_length,
                            "Word_Length": word_length
                        })

    if not data_rows:
        return

    df = pd.DataFrame(data_rows)
    df.to_csv(OUTPUT_DIR / "raw_lengths.csv", index=False)
    
    global_summary = df.groupby('Model')['Word_Length'].mean().round(2).to_dict()
    models = list(global_summary.keys())
    qlora_models = [m for m in models if "finetuned" in m.lower()]
    
    with open(OUTPUT_DIR / "analysis_summary.txt", "w", encoding="utf-8") as f:
        f.write("GLOBAL VERBOSITY SUMMARY\n\n")
        for qlora_model in qlora_models:
            base_model = re.sub(r'_?finetuned', '_base', qlora_model, flags=re.IGNORECASE)
            if base_model in global_summary:
                f.write(f"{base_model}: {global_summary[base_model]} words | {qlora_model}: {global_summary[qlora_model]} words\n")
        
        f.write("\nSHOT ANALYSIS (ICL IMPACT)\n\n")
        df_shots = df.groupby(['Model', 'Shot'])['Word_Length'].mean().round(2).reset_index()
        for qlora_model in sorted(qlora_models):
            base_model = re.sub(r'_?finetuned', '_base', qlora_model, flags=re.IGNORECASE)
            f.write(f"Model Pair: {base_model} vs {qlora_model}\n")
            
            if base_model in df_shots['Model'].values:
                shots_list = sort_shots(df_shots[df_shots['Model'] == base_model]['Shot'].unique())
                for shot in shots_list:
                    val = df_shots[(df_shots['Model'] == base_model) & (df_shots['Shot'] == shot)]['Word_Length'].values
                    val_str = val[0] if len(val) > 0 else "N/A"
                    note = " (Shows ICL learning to stop)" if shot == shots_list[-1] else ""
                    f.write(f"- {base_model} {shot} length: {val_str} words{note}\n")
            
            if qlora_model in df_shots['Model'].values:
                shots_list = sort_shots(df_shots[df_shots['Model'] == qlora_model]['Shot'].unique())
                for shot in shots_list:
                    val = df_shots[(df_shots['Model'] == qlora_model) & (df_shots['Shot'] == shot)]['Word_Length'].values
                    val_str = val[0] if len(val) > 0 else "N/A"
                    note = " (Shows native constraint)" if shot == "0SHOT" else ""
                    f.write(f"- {qlora_model} {shot} length: {val_str} words{note}\n")
            f.write("\n")

        f.write("PROMPT VARIANCE ANALYSIS\n\n")
        df_prompts = df.groupby(['Model', 'Prompt'])['Word_Length'].mean().round(2).reset_index()
        for model in sorted(models):
            std_dev = df_prompts[df_prompts['Model'] == model]['Word_Length'].std()
            std_dev_val = round(std_dev, 2) if pd.notna(std_dev) else 0.0
            f.write(f"{model} prompt variance (Std Dev): {std_dev_val} words\n")

    plot_length_evolution(df, OUTPUT_FIG_DIR)

if __name__ == "__main__":
    main()