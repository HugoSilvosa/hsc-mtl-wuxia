import os
import re
import argparse


def procesar_condor(nombre_archivo: str, out_dir: str):
    
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    patron = re.compile(r'^(第[\d一二三四五六七八九十百千万零]+回)')
    patron_en = re.compile(r'^Chapter\s+\d+', re.IGNORECASE)

    carpeta_salida = out_dir
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    contador = 0  # Inicializamos en 0; así el primer capítulo se numerará como 1
    anterior_titulo = None

    for linea in lineas:
        linea_stripped = linea.strip()
        match = patron.match(linea_stripped)

        if patron_en.match(linea_stripped):
            continue

        if match:
            titulo_actual = match.group(1)

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


def procesar_guzhenren(nombre_archivo: str, out_dir: str):
    
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    patron = re.compile(r'^第[\d一二三四五六七八九十百千万零]+[章节](?:[:：\s])')

    carpeta_salida = out_dir
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    contador = 0  # Inicializamos en 0; así el primer capítulo se numerará como 1
    anterior_titulo = None

    for linea in lineas:
        linea_stripped = linea.strip()
        match = patron.match(linea_stripped)

        if match:
            titulo_actual = match.group(0)  # conserva exactamente lo que hacía el regex

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


def procesar_awe(nombre_archivo: str, out_dir: str):
    
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Detecta líneas como: 第1314章 你的选择
    patron = re.compile(r'(第[\d一二三四五六七八九十百千万零]+[章节])')

    carpeta_salida = out_dir
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesar novelas en chino y dividir por capítulos")
    parser.add_argument("--novela", choices=["condor", "gu", "awe"], required=True,
                        help="Nombre de la novela a procesar")
    parser.add_argument("--input", required=True,
                        help="Nombre del archivo dentro de data/<novela>/raw/")
    parser.add_argument("--outname", default="segmented/chapter",
                        help="Nombre de la subcarpeta de salida dentro de data/<novela>/")
    args = parser.parse_args()

    # Para AWE: python scripts\preprocessing\chinese.pychinese.py --novela awe --input awe_ch.txt --outname segmented/chapter
    if args.novela == "awe":
        base_dir = os.path.join("data", args.novela, "raw")
        input_file = os.path.join(base_dir, args.input)
        out_dir = os.path.join("data", args.novela, args.outname)
        procesar_awe(input_file, out_dir)

    if args.novela == "condor":
        base_dir = os.path.join("data", args.novela, "raw")
        input_file = os.path.join(base_dir, args.input)
        out_dir = os.path.join("data", args.novela, args.outname)
        procesar_condor(input_file, out_dir)
        
    elif args.novela == "gu":
        base_dir = os.path.join("data", args.novela, "raw")
        input_file = os.path.join(base_dir, args.input)
        out_dir = os.path.join("data", args.novela, args.outname)
        procesar_guzhenren(input_file, out_dir)

