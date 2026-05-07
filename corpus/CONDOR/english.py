import os
import re

def corregir_espacios(palabra):
    # Corrige cosas como "h ad" -> "had", "Wu c lan" -> "Wu clan"
    # Solo un espacio entre letras (no en casos normales como dos palabras reales)
    return re.sub(r'(\b\w)\s+(\w\b)', r'\1\2', palabra)

def proccess_en(nombre_archivo, out_dir):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    # Patrones flexibles
    patron = re.compile(r'^Chapter[\s]*(\d+)[\s.:：\-–]*', re.IGNORECASE)

    carpeta_salida = out_dir
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    contenido = []
    cap_anterior = None
    contador = 0

    for i in range(len(lineas)):
        linea = lineas[i].strip()
        match = patron.match(linea)

        if match:
            cap_actual = int(match.group(1))

            if cap_actual != cap_anterior:
                if contenido:
                    cap_nombre = cap_anterior - 1 if cap_anterior >= 1215 else cap_anterior
                    nombre_archivo_salida = os.path.join(carpeta_salida, f"{cap_nombre}en.txt")
                    with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
                        f_out.write("".join(contenido))
                contenido = [lineas[i]]
                cap_anterior = cap_actual
                contador += 1
            else:
                continue
        else:
            if contenido:
                # Corregir espacios antes de añadir la línea
                linea_corregida = corregir_espacios(lineas[i])
                contenido.append(linea_corregida)

    # Último capítulo
    if contenido and cap_anterior is not None:
        nombre_archivo_salida = os.path.join(carpeta_salida, f"{cap_anterior-1}en.txt")
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as f_out:
            f_out.write("".join(contenido))

    print(f"{nombre_archivo} -> {contador} capítulos extraídos")

if __name__ == '__main__':
    carpeta_salida = 'Condor1'
    proccess_en("english_condor_1.txt", out=carpeta_salida)
    carpeta_salida = 'Condor2'
    proccess_en("english_condor_2.txt", out=carpeta_salida)
    carpeta_salida = 'Condor3'
    proccess_en("english_condor_2.txt", out=carpeta_salida)
