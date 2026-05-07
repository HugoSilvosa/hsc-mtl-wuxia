import os
import re

def proccess_ch(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Detecta líneas como: 第1314章 你的选择
    patron = re.compile(r'(第[\d一二三四五六七八九十百千万零]+[章节])')

    carpeta_salida = 'chapter'
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    contador = 0
    anterior_titulo = None

    for linea in lineas:
        linea_stripped = linea.strip()
        match = patron.match(linea_stripped)

        if match:
            titulo_actual = match.group(1)  # Solo captura "第xxx章"

            if titulo_actual != anterior_titulo:
                if contenido:
                    nombre_archivo_salida = os.path.join(carpeta_salida, f"{contador}ch.txt")
                    with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
                        f_out.write("".join(contenido))
                contador += 1
                contenido = [titulo_actual + "\n"]  # Solo guarda "第xxx章"
                anterior_titulo = titulo_actual
            else:
                continue  # línea duplicada
        else:
            if contenido:
                contenido.append(linea)

    # Guardar el último capítulo
    if contenido:
        nombre_archivo_salida = os.path.join(carpeta_salida, f"{contador}ch.txt")
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
            f_out.write("".join(contenido))

    print(f"{nombre_archivo} -> {contador} capítulos extraídos")

if __name__ == '__main__':
    proccess_ch("awe_ch.txt")
