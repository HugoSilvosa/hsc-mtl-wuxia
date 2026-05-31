import argparse
import pickle
import time
import jieba
from tqdm import tqdm
from nltk.translate import AlignedSent, ibm1, ibm2, ibm3
from datasets import load_from_disk

RUTA_DATASET = r"C:\Users\Usuario\Desktop\TFG\CORPUS\processed_data\wuxia_selected_100000"

PLANTILLA_MODELO = r"C:\Users\Usuario\Desktop\TFG\CORPUS\models\modelo_wuxia_{}.pkl"
PLANTILLA_SALIDA = r"C:\Users\Usuario\Desktop\TFG\CORPUS\src\SMT\traducciones_test_{}.txt"


def cargar_datos_seguros():
    """Carga el dataset y maneja si tiene particiones (train/test) o es plano"""
    dataset = load_from_disk(RUTA_DATASET)
    if hasattr(dataset, 'keys'):
        nombre_particion = list(dataset.keys())[0]
        return dataset[nombre_particion], dataset
    return dataset, dataset

def entrenar(tamanio_entrenamiento, tipo_modelo):
    print(f"\n--- MODO ENTRENAMIENTO: {tipo_modelo.upper()} ---")
    dataset_plano, _ = cargar_datos_seguros()
    
    total_disponible = len(dataset_plano)
    if tamanio_entrenamiento == 0 or tamanio_entrenamiento > total_disponible:
        tamanio_entrenamiento = total_disponible
        
    print(f"Preparando {tamanio_entrenamiento} frases para entrenar...")
    dataset_train = dataset_plano.select(range(tamanio_entrenamiento))
    
    corpus_entrenamiento = []
    
    for item in tqdm(dataset_train, desc="Alineando textos"):
        try:
            ingles_crudo = item['translation']['en']
            chino_crudo = item['translation']['zh']
        except (KeyError, TypeError):
            ingles_crudo = item['en']
            chino_crudo = item['zh']

        ingles = ingles_crudo.lower().split()
        chino = list(jieba.cut(chino_crudo.replace(" ", "")))
        corpus_entrenamiento.append(AlignedSent(ingles, chino))

    print(f"\nEntrenando {tipo_modelo.upper()} con {len(corpus_entrenamiento)} frases...")
    inicio = time.time()
    

    if tipo_modelo == "ibm1":
        modelo_smt = ibm1.IBMModel1(corpus_entrenamiento, 10)
    elif tipo_modelo == "ibm2":
        modelo_smt = ibm2.IBMModel2(corpus_entrenamiento, 10)
    elif tipo_modelo == "ibm3":
        modelo_smt = ibm3.IBMModel3(corpus_entrenamiento, 2)
    else:
        raise ValueError("Modelo no soportado.")
    
    fin = time.time()
    mins, segs = divmod(int(fin - inicio), 60)
    print(f"Entrenamiento completado en {mins}m {segs}s")

    # Extraemos solo el diccionario de traducción
    tabla_limpia = {}
    for palabra_e, dict_probabilidades in modelo_smt.translation_table.items():
        tabla_limpia[palabra_e] = dict(dict_probabilidades)

    ruta_modelo = PLANTILLA_MODELO.format(tipo_modelo)
    print(f"Guardando tabla de traducción limpia en: {ruta_modelo}")
    with open(ruta_modelo, 'wb') as f:
        pickle.dump(tabla_limpia, f)
    print("Modelo guardado correctamente\n")


def inferir(tamanio_inferencia, tipo_modelo):
    print(f"\n--- MODO INFERENCIA: {tipo_modelo.upper()} ---")
    ruta_modelo = PLANTILLA_MODELO.format(tipo_modelo)
    ruta_salida = PLANTILLA_SALIDA.format(tipo_modelo)
    
    print(f"Cargando tabla estadística desde {ruta_modelo}...")
    try:
        with open(ruta_modelo, 'rb') as f:
            tabla_traduccion = pickle.load(f) 
    except FileNotFoundError:
        print(f"ERROR: No se encontró el modelo {tipo_modelo.upper()}.")
        return

    dataset_plano, dataset_completo = cargar_datos_seguros()
    
    if hasattr(dataset_completo, 'keys') and 'test' in dataset_completo.keys():
        dataset_test = dataset_completo['test']
        print("Usando partición 'test' oficial.")
    else:
        print("Usando el final del dataset principal como test.")
        dataset_test = dataset_plano.select(range(len(dataset_plano) - 1000, len(dataset_plano)))

    total_test = len(dataset_test)
    if tamanio_inferencia == 0 or tamanio_inferencia > total_test:
        tamanio_inferencia = total_test
        
    dataset_test = dataset_test.select(range(tamanio_inferencia))
    print(f"Se van a traducir {tamanio_inferencia} frases...")

    def traducir(frase_china, top_n=3):
        palabras_chinas = list(jieba.cut(frase_china.replace(" ", "")))
        traduccion = []
        detalles = [] 
        
        for palabra_c in palabras_chinas:
            candidatos = []
            
            # Recorremos la tabla buscando todas las palabras en inglés que traduzcan esta palabra china
            for palabra_e, probabilidades_origen in tabla_traduccion.items():
                prob = probabilidades_origen.get(palabra_c, 0.0)
                if prob > 0.0:
                    candidatos.append((palabra_e, prob))
            
            # Ordenamos los candidatos de mayor a menor probabilidad
            candidatos_ordenados = sorted(candidatos, key=lambda x: x[1], reverse=True)
            
            if candidatos_ordenados and candidatos_ordenados[0][1] > 0.01:
                # El ganador sigue siendo el primero
                mejor_palabra_e, max_prob = candidatos_ordenados[0]
                traduccion.append(mejor_palabra_e)
                
                # Construimos el Top N 
                top_candidatos = candidatos_ordenados[:top_n]
                strings_candidatos = [f"{pal_e}({pr * 100:.2f}%)" for pal_e, pr in top_candidatos]
                
                detalles.append(f"{palabra_c}[{'|'.join(strings_candidatos)}]")
            else:
                traduccion.append(f"[{palabra_c}]")
                detalles.append(f"[{palabra_c}](UNK)")
                
        return " ".join(traduccion), "  ".join(detalles)

    print(f"Generando archivo de salida en: {ruta_salida}")
    with open(ruta_salida, 'w', encoding='utf-8') as f_out:
        f_out.write("ORIGINAL_CHINO ; ESPERADA_INGLES ; GENERADA_SMT ; DETALLES_PROBABILIDAD\n")
        
        for item in tqdm(dataset_test, desc="Traduciendo"):
            try:
                chino_crudo = item['translation']['zh']
                ingles_esperado = item['translation']['en']
            except (KeyError, TypeError):
                chino_crudo = item['zh']
                ingles_esperado = item['en']
                
            trad_generada, desglose_prob = traducir(chino_crudo, top_n=10) 
            
            # Limpieza
            chino_limpio = chino_crudo.replace('\n', ' ').replace(';', ',')
            ingles_limpio = ingles_esperado.replace('\n', ' ').replace(';', ',')
            trad_limpia = trad_generada.replace('\n', ' ').replace(';', ',')
            desglose_limpio = desglose_prob.replace('\n', ' ').replace(';', ',')
            
            # Formateamos la línea con las 4 columnas
            linea_salida = f"{chino_limpio} ; {ingles_limpio} ; {trad_limpia} ; {desglose_limpio}"
            f_out.write(linea_salida + "\n")
            
    print(f"\nDone\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline SMT multiparadigma para TFG")
    
    parser.add_argument("modo", choices=["train", "infer"], help="Modo de ejecución: 'train' o 'infer'")
    
    parser.add_argument("--model", choices=["ibm1", "ibm2", "ibm3"], default="ibm2", 
                        help="Modelo estadístico a utilizar (defecto: ibm2)")
    
    parser.add_argument("--train_size", type=int, default=0, help="Nº de frases para entrenar (0 = todo)")
    parser.add_argument("--infer_size", type=int, default=0, help="Nº de frases para traducir en test (0 = todo)")

    args = parser.parse_args()

    if args.modo == "train":
        entrenar(args.train_size, args.model)
    elif args.modo == "infer":
        inferir(args.infer_size, args.model)
        
        
        
# python test.py train --model ibm1 --train_size 5000
# python test.py infer --model ibm1 --infer_size 200