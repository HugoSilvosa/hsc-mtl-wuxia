import pandas as pd
import glob
import os

def analyze(carpeta_archivos="archivos_evaluados", archivo_salida="resultados_evaluadores.txt"):
    try:
        ruta_busqueda = os.path.join(carpeta_archivos, "*.csv")
        archivos_csv = glob.glob(ruta_busqueda)
        
        if not archivos_csv:
            print(f"No se encontraron archivos en la carpeta '{carpeta_archivos}'.")
            return
            
        print(f"Leyendo y combinando {len(archivos_csv)} archivos...\n")
        
        lista_dfs = []
        for archivo in archivos_csv:
            try:
                lista_dfs.append(pd.read_csv(archivo))
            except Exception as e:
                print(f"Error leyendo el archivo {archivo}: {e}")
                
        df = pd.concat(lista_dfs, ignore_index=True)
        
        metricas_base = ['Fidelidad', 'Calidad', 'Dominio', 'Alucinacion']
        evaluadores = set()
        
        for col in df.columns:
            for metrica in metricas_base:
                if metrica.lower() in col.lower():
                    if '_' in col:
                        evaluador = col.split('_')[0]
                        # Filtramos variables temporales o de traducción
                        if evaluador not in ['Traduccion', 'Texto', 'ID']: 
                            evaluadores.add(evaluador)
                    else:
                        evaluadores.add('Propio')
                    break
        
        columnas_agrupacion = ['Arquitectura', 'Estado_Modelo', 'Tipo_Input']
        for col in columnas_agrupacion:
            if col not in df.columns:
                print(f"Error: La columna '{col}' no existe en los archivos.")
                return

        with open(archivo_salida, "w", encoding="utf-8") as f:
            f.write("=== RESULTADOS MEDIOS DE LA EVALUACIÓN POR JUEZ ===\n")
            f.write("="*60 + "\n\n")
            
            for evaluador in sorted(evaluadores):
                f.write(f" EVALUADOR: {evaluador.upper()} \n")
                
                # Buscar solo las columnas de métricas de este evaluador
                cols_evaluador = []
                diccionario_renombres = {}
                
                for metrica in metricas_base:
                    for col in df.columns:
                        if metrica.lower() in col.lower():
                            if evaluador == 'Propio' and '_' not in col:
                                cols_evaluador.append(col)
                                diccionario_renombres[col] = metrica.upper()
                            elif evaluador != 'Propio' and col.startswith(evaluador + '_'):
                                cols_evaluador.append(col)
                                diccionario_renombres[col] = metrica.upper()
                
                if not cols_evaluador:
                    f.write("No hay datos de métricas para este evaluador.\n\n")
                    continue
                    
                # Calcular las medias para este juez
                df_subset = df[columnas_agrupacion + cols_evaluador].copy()
                
                # Convertir a numérico por si hay algún error de formato, ignorando vacíos
                for c in cols_evaluador:
                    df_subset[c] = pd.to_numeric(df_subset[c], errors='coerce')
                    
                resultados = df_subset.groupby(columnas_agrupacion)[cols_evaluador].mean().reset_index()
                resultados[cols_evaluador] = resultados[cols_evaluador].round(2)
                
                resultados.rename(columns=diccionario_renombres, inplace=True)
                
                f.write(resultados.to_string(index=False))
                f.write("\n\n" + "-"*60 + "\n\n")
        
        print(f"Done: {archivo_salida}")
            
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    analyze(carpeta_archivos='archivos_evaluados', archivo_salida='resultados_evaluadores.txt')