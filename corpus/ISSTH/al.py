import re

def es_hilera_de_guiones(linea):
    # Devuelve True si la línea contiene al menos 4 guiones consecutivos (ignorando espacios)
    return re.search(r'-{3,}', linea.strip()) is not None

def limpiar_archivo(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    salida = []
    borrados = []
    i = 0
    total_lineas = len(lineas)

    while i < total_lineas:
        if es_hilera_de_guiones(lineas[i]):
            inicio = i
            j = i + 1
            # Buscar una segunda hilera de guiones a menos de 22 líneas totales (20 entre ellas + 2 bordes)
            while j < total_lineas and (j - inicio <= 21):
                if es_hilera_de_guiones(lineas[j]):
                    if j - inicio - 1 <= 20:
                        bloque = lineas[inicio:j+1]
                        borrados.append(''.join(bloque))
                        i = j + 1  # Saltar el bloque completo
                        break
                j += 1
            else:
                # No se encontró cierre válido
                salida.append(lineas[i])
                i += 1
        else:
            salida.append(lineas[i])
            i += 1

    # Guardar archivo limpio
    with open('salida.txt', 'w', encoding='utf-8') as f:
        f.writelines(salida)

    # Guardar log de bloques eliminados
    with open('log_borrados.txt', 'w', encoding='utf-8') as f:
        f.write("=== BLOQUES ELIMINADOS ===\n\n")
        for idx, bloque in enumerate(borrados, 1):
            f.write(f"--- BLOQUE {idx} ---\n{bloque}\n")

    print(f"Proceso completado: {len(borrados)} bloques eliminados.")
    print("Revisa 'salida.txt' y 'log_borrados.txt'.")

# Ejecutar con archivo de entrada

# Ejemplo de uso
limpiar_archivo('salida.txt')
