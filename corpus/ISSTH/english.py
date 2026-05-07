import os
import re

def corregir_espacios(palabra):
    return re.sub(r'(\b\w)\s+(\w\b)', r'\1\2', palabra)

def proccess_en(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Patrón que detecta capítulo y extrae número (ej. Chapter 123: Title)
    patron = re.compile(r'Chapter\s+(\d+)[^\n]*', re.IGNORECASE)

    carpeta_salida = 'chapter'
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    cap_anterior = None
    contador = 0

    for i in range(len(lineas)):
        linea = lineas[i].strip()
        match = patron.search(linea)

        if match:
            cap_actual = int(match.group(1))

            if cap_actual != cap_anterior:
                if contenido:
                    nombre_archivo_salida = os.path.join(carpeta_salida, f"{cap_anterior}en.txt")
                    with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
                        f_out.write("".join(contenido))
                contenido = [lineas[i]]
                cap_anterior = cap_actual
                contador += 1
        else:
            if contenido:
                linea_corregida = corregir_espacios(lineas[i])
                contenido.append(linea_corregida)

    # Guardar el último capítulo
    if contenido and cap_anterior is not None:
        nombre_archivo_salida = os.path.join(carpeta_salida, f"{cap_anterior}en.txt")
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
            f_out.write("".join(contenido))

    print(f"{nombre_archivo} -> {contador} capítulos extraídos")

if __name__ == '__main__':
    proccess_en("issth_en_post.txt")
