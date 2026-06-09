import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

input_file = '../tiempos_entrenamiento.txt'
output_dir = '../../fig/time/train'

def generar_graficas():
    os.makedirs(output_dir, exist_ok=True)

    path_to_read = input_file if os.path.exists(input_file) else '../tiempos_entrenamiento'
    df = pd.read_csv(path_to_read, sep=';', comment='#')

    df = df.sort_values(by='Tiempo_Entrenamiento_Horas', ascending=True)

    colors = {'NMT': '#2c7fb8', 'LLM': '#f03b20'}
    bar_colors = df['Arquitectura'].map(colors)

    def plot_chart(lang):
        plt.figure(figsize=(8, 4))
        
        plt.barh(df['Modelo'], df['Tiempo_Entrenamiento_Horas'], color=bar_colors, edgecolor='black', linewidth=0.5)
        
        if lang == 'es':
            title = 'Tiempo de entrenamiento por modelo'
            xlabel = 'Tiempo (horas)'
            ylabel = 'Modelo'
            legend_title = 'Arquitectura'
            filename = 'entrenamiento_es.png'
        else:
            title = 'Training time per model'
            xlabel = 'Time (hours)'
            ylabel = 'Model'
            legend_title = 'Architecture'
            filename = 'training_en.png'

        plt.xlabel(xlabel, fontsize=13)
        plt.ylabel(ylabel, fontsize=13)

        # Leyenda
        legend_elements = [Patch(facecolor=colors['NMT'], edgecolor='black', label='NMT'),
                        Patch(facecolor=colors['LLM'], edgecolor='black', label='LLM')]
        plt.legend(handles=legend_elements, title=legend_title, loc='lower right', framealpha=0.9)
        
        # Estilos y guardado
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.gca().set_axisbelow(True)
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Gráfica generada: {output_path}")

    plot_chart('es')
    plot_chart('en')

if __name__ == '__main__':
    generar_graficas()