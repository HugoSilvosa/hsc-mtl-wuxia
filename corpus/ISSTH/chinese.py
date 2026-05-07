import os
import re

def proccess_ch(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    patron = re.compile(r'第[\d一二三四五六七八九十百千万零]+[章节]')
    carpeta_salida = 'chapter'
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    contador = 0  # Inicializamos en 0; así el primer capítulo se numerará como 1
    anterior_titulo = None

    for linea in lineas:
        linea_stripped = linea.strip()
        match = patron.match(linea_stripped)

        if match:
            titulo_actual = match.group(0)

            if titulo_actual != anterior_titulo:
                # Guardar el capítulo anterior si ya se acumuló contenido
                if contenido:
                    nombre_archivo_salida = os.path.join(carpeta_salida, f"{contador}ch.txt")
                    with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
                        f_out.write("".join(contenido))
                contador += 1
                contenido = [linea]
                anterior_titulo = titulo_actual
            else:
                continue  # línea duplicada, ignoramos
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
    proccess_ch("issth_ch_post.txt")
