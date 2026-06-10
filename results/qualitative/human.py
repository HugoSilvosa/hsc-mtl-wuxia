import pandas as pd
import os
import glob
import numpy as np

def run():
    print(" ----\n EVALUACIÓN DE TRADUCCIONES\n ----")
    evaluador_id = input("\nPor favor, introduce tu Nombre o ID de evaluador: ").strip()
    
    if not evaluador_id:
        print("Error: El ID no puede estar vacío.")
        return

    ruta_entrada = os.path.join("results", "cualitativa", "archivos_separados")
    ruta_salida_base = os.path.join("results", "cualitativa", "archivos_human", evaluador_id)

    if not os.path.exists(ruta_entrada):
        print(f"Error: No se encuentra la carpeta de origen '{ruta_entrada}'.")
        return

    archivos_csv = glob.glob(os.path.join(ruta_entrada, "*.csv"))
    if not archivos_csv:
        print(f"No hay archivos CSV en la carpeta '{ruta_entrada}'.")
        return

    print(f"\nCargando {len(archivos_csv)} archivos...\n\n")
    df = pd.concat([pd.read_csv(f) for f in archivos_csv], ignore_index=True)

    metricas = ['Fidelidad', 'Calidad', 'Dominio', 'Alucinacion']
    
    columnas_reales = df.columns.tolist()
    for metrica in metricas:
        col_encontrada = next((c for c in columnas_reales if metrica.lower() in c.lower()), None)
        if col_encontrada:
            df[col_encontrada] = np.nan  
        else:
            df[metrica.upper()] = np.nan 

    df = df.sample(frac=1, random_state=None).reset_index(drop=True)

    print("Instrucciones: Escribe tus puntuaciones y presiona Enter.")
    print("Si necesitas detenerte y guardar tu progreso, escribe 'salir'.\n\n")

    # 6. Bucle interactivo
    filas_procesadas = 0
    for index, row in df.iterrows():
        print(f"\n [ SEGMENTO {index + 1} / {len(df)} ] ")
        
        texto_raw = row.get('texto_raw', row.get('Texto_Raw', row.get('TEXTO_RAW', 'N/A')))
        texto_input = row.get('texto_input', row.get('Texto_Input', row.get('TEXTO_INPUT', 'N/A')))
        texto_output = row.get('texto_output', row.get('Texto_Output', row.get('TEXTO_OUTPUT', 'N/A')))

        print(f"\n[TEXTO RAW (Original)]\n{texto_raw}")
        print(f"\n[TEXTO INPUT (Traducción Profesional)]\n{texto_input}")
        print(f"\n[TEXTO OUTPUT (Inferencia a evaluar)]\n{texto_output}\n")

        try:
            # Inputs
            fidelidad = input("Fidelidad (0-3): ")
            if fidelidad.lower() == 'salir': break
            
            calidad = input("Calidad (0-3): ")
            if calidad.lower() == 'salir': break
            
            dominio = input("Dominio (0-3): ")
            if dominio.lower() == 'salir': break
            
            alucinacion = input("Alucinación (0 o 1): ")
            if alucinacion.lower() == 'salir': break

            # Guardamos las respuestas localizando las columnas correctas
            for c in df.columns:
                if 'fidelidad' in c.lower(): df.at[index, c] = float(fidelidad)
                if 'calidad' in c.lower(): df.at[index, c] = float(calidad)
                if 'dominio' in c.lower(): df.at[index, c] = float(dominio)
                if 'alucinacion' in c.lower(): df.at[index, c] = int(alucinacion)

            filas_procesadas += 1

        except ValueError:
            print("\nError: Debes introducir números válidos. Este segmento se dejará en blanco.")
            continue

    if filas_procesadas > 0 or input("\n¿Quieres generar los archivos de salida de todos modos? (s/n): ").lower() == 's':
        os.makedirs(ruta_salida_base, exist_ok=True)
        print(f"\nProcesando y dividiendo el archivo final en 6 partes...")
        
        df_dividido = np.array_split(df, 6)
        
        for i, trozo_df in enumerate(df_dividido):
            nombre_archivo = f"evaluacion_{evaluador_id}_parte_{i+1}.csv"
            ruta_final = os.path.join(ruta_salida_base, nombre_archivo)
            
            trozo_df.to_csv(ruta_final, index=False, encoding='utf-8')
            
        print(f"Se han guardado 6 archivos en:\n{ruta_salida_base}")
    else:
        print("\nOperación cancelada. No se han modificado ni creado archivos.")

if __name__ == "__main__":
    run()