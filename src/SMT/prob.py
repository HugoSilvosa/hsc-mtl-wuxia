import pickle

RUTA_MODELO = r"C:\Users\Usuario\Desktop\TFG\CORPUS\models\modelo_wuxia_ibm2.pkl"

print("Cargando el cerebro estadístico del modelo...")
with open(RUTA_MODELO, 'rb') as f:
    # Recuerda que guardamos un diccionario: tabla[ingles][chino] = probabilidad
    tabla_traduccion = pickle.load(f)

def consultar_palabra(palabra_china, top_n=5):
    """Busca todas las traducciones posibles para una palabra china y las ordena por probabilidad"""
    resultados = []
    
    # Recorremos todo el diccionario de inglés
    for palabra_e, probabilidades_origen in tabla_traduccion.items():
        # Si la palabra china existe en las probabilidades de esta palabra inglesa
        if palabra_china in probabilidades_origen:
            prob = probabilidades_origen[palabra_china]
            # Filtramos el ruido estadístico (probabilidades minúsculas)
            if prob > 0.001: 
                resultados.append((palabra_e, prob))
                
    # Ordenamos de mayor a menor probabilidad
    resultados.sort(key=lambda x: x[1], reverse=True)
    
    # Devolvemos solo las 'top_n' mejores
    return resultados[:top_n]

# --- VAMOS A HACER CONSULTAS PARA TU TFG ---
# Pon aquí las palabras clave de tu novela que quieras analizar
palabras_a_consultar = ["魔头", "杀", "剑", "宗门"] # Ej: Demonio, Matar, Espada, Secta

print("\n--- ANÁLISIS DE PROBABILIDADES ESTADÍSTICAS ---")
for palabra in palabras_a_consultar:
    opciones = consultar_palabra(palabra)
    
    print(f"\nPalabra original: 【 {palabra} 】")
    if not opciones:
        print("  -> (El modelo no ha aprendido esta palabra o la probabilidad es casi 0)")
    else:
        for i, (traduccion, probabilidad) in enumerate(opciones, 1):
            # Convertimos el decimal (0.85) a porcentaje (85.00%) para que sea más legible
            porcentaje = probabilidad * 100
            print(f"  {i}. {traduccion:<15} -> {porcentaje:>6.2f} %")