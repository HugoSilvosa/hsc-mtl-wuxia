import os
import re

def corregir_espacios(palabra):
    # Corrige cosas como "h ad" -> "had", "Wu c lan" -> "Wu clan"
    # Solo un espacio entre letras (no en casos normales como dos palabras reales)
    return re.sub(r'(\b\w)\s+(\w\b)', r'\1\2', palabra)

def proccess_en(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Detecta líneas como: 0000 chapter-1
    patron = re.compile(r'^\d{4}\s+(chapter-\d+)', re.IGNORECASE)

    carpeta_salida = 'chapter'
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    cap_anterior = None
    contador = 0

    for i in range(len(lineas)):
        linea = lineas[i].strip()
        match = patron.match(linea)

        if match:
            chapter_text = match.group(1)  # "chapter-1"
            chapter_number = int(re.search(r'\d+', chapter_text).group())

            if chapter_number != cap_anterior:
                if contenido:
                    nombre_archivo_salida = os.path.join(carpeta_salida, f"{cap_anterior}en.txt")
                    with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
                        f_out.write("".join(contenido))
                contenido = [chapter_text + "\n"]  # Agregamos solo "chapter-X"
                cap_anterior = chapter_number
                contador += 1
        else:
            if cap_anterior is not None:
                linea_corregida = corregir_espacios(lineas[i])
                contenido.append(linea_corregida)

    # Guardar el último capítulo
    if contenido and cap_anterior is not None:
        nombre_archivo_salida = os.path.join(carpeta_salida, f"{cap_anterior}en.txt")
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
            f_out.write("".join(contenido))

    print(f"{nombre_archivo} -> {contador} capítulos extraídos")

if __name__ == '__main__':
    proccess_en("awe_en.txt")
