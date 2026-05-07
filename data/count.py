# contar_palabras_misma_carpeta.py

import os

def contar_palabras(archivo):
    """Cuenta las palabras en un archivo de texto."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            texto = f.read()
            palabras = texto.split()
            return len(palabras)
    except Exception as e:
        print(f"Error al procesar '{archivo}': {e}")
        return None

if __name__ == "__main__":
    # Obtener la carpeta donde está el script
    carpeta = os.path.dirname(os.path.abspath(__file__))

    print("Conteo de palabras por archivo:\n" + "-"*40)

    archivos_txt = [f for f in os.listdir(carpeta) if f.lower().endswith(".txt")]

    if not archivos_txt:
        print("No se encontraron txt")
    else:
        for nombre in archivos_txt:
            ruta = os.path.join(carpeta, nombre)
            cantidad = contar_palabras(ruta)
            if cantidad is not None:
                print(f"{nombre}: {cantidad} palabras")

    print("-"*40)
    print("Proceso completado.")
