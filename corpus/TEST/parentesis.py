import re
import argparse
import os

# Patrón para detectar:
# 1) Comillas (‘ ’ “ ” ' ")
# 2) Pinyin (letras y espacios)
# 3) Traducción entre corchetes [ ... ]
PATTERN = re.compile(
    r"(?P<open>['\"“‘])"           # comilla de apertura
    r"(?P<pinyin>[A-Za-z\s]+?)"    # pinyin: letras y espacios
    r"(?P<close>['\"”’])"          # comilla de cierre
    r"\s*\["                       # corchete de apertura
    r"(?P<trans>[^\]]+)"           # traducción: cualquier cosa menos ]
    r"\]"                          # corchete de cierre
)

def procesar_archivo(input_path: str, output_path: str, log_path: str):
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out, \
         open(log_path, 'w', encoding='utf-8') as f_log:

        for lineno, linea in enumerate(f_in, start=1):
            def reemplazo(m: re.Match) -> str:
                original = m.group(0)
                nueva = f"{m.group('open')}{m.group('trans')}{m.group('close')}"
                # Escribimos en el log
                f_log.write(f"Línea {lineno}: \"{original}\" → \"{nueva}\"\n")
                return nueva

            nueva_linea = PATTERN.sub(reemplazo, linea)
            f_out.write(nueva_linea)

    print(f"✅ Procesado completo. Cambios guardados en '{log_path}'.")

if __name__ == "__main__":


    procesar_archivo("test.txt", "testt.txt", "log.txt")
