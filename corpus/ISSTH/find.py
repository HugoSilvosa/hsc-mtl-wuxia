import re

# Conversor de números chinos a enteros
chinese_map = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,
               '十':10,'百':100,'千':1000,'万':10000}

def chinese_to_int(chinese):
    if chinese.isdigit():
        return int(chinese)
    
    unit = 1
    result = 0
    num = 0
    for char in reversed(chinese):
        if char in chinese_map:
            val = chinese_map[char]
            if val >= 10:
                if num == 0:
                    num = 1
                result += val * unit
                unit = val
                num = 0
            else:
                num += val * unit
        else:
            continue
    result += num
    return result

def buscar_capitulos_chinos(filepath, output_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        texto = f.read()

    # patron = re.compile(r'(第)([\d一二三四五六七八九十百千万零]+)([章节])')
    patron = re.compile(r'(Chapter\s+)([\d]+)', re.IGNORECASE)
    matches = []

    for match in patron.finditer(texto):
        cap_completo = match.group(0)
        cap_num_str = match.group(2)
        cap_num_int = chinese_to_int(cap_num_str)
        posicion = match.start()
        matches.append((cap_completo, cap_num_int, posicion))

    lines = []
    lines.append(f"{filepath} -> {len(matches)} capítulos detectados\n")
    for i, (cap, cap_num, pos) in enumerate(matches, 1):
        status = ""
        if cap_num != i:
            if cap_num < i:
                status = "⚠️ Duplicado o retroceso"
            else:
                status = "⚠️ Salto o adelantado"
        line = f"{i:04}: {cap:<10} (Núm: {cap_num:>4}) Pos: {pos:<8} {status}"
        print(line)
        lines.append(line)

    # Guardar resultados en archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\nResultados guardados en: {output_path}")

# Ejecutar con archivo original y archivo de salida
buscar_capitulos_chinos("issth_en_post.txt", "capitulos_detectados.txt")
