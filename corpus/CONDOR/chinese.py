import os
import re

def proccess_ch(nombre_archivo, out_dir):
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

if __name__ == '__main__':
    carpeta_salida = 'Condor1'
    proccess_ch("chinese_condor_1.txt", out_dir=carpeta_salida)
    carpeta_salida = 'Condor2'
    proccess_ch("chinese_condor_2.txt", out_dir=carpeta_salida)
    carpeta_salida = 'Condor3'
    proccess_ch("chinese_condor_3.txt", out_dir=carpeta_salida)
