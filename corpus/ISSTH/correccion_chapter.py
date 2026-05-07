import re

# Cargar archivos
with open('issth_en.txt', 'r', encoding='utf-8') as f:
    english_text = f.read()

with open('issth_ch.txt', 'r', encoding='utf-8') as f:
    chinese_text = f.read()

# Regex para encontrar capítulos
english_pattern = re.compile(r'(Chapter\s+)(\w+)', re.IGNORECASE)
chinese_pattern = re.compile(r'(第)[\d一二三四五六七八九十百千万零]+([章节])')

# Reemplazar capítulos en inglés con su orden
def replace_english(match, counter=[1]):
    result = f'{match.group(1)}{counter[0]}'
    counter[0] += 1
    return result

# Reemplazar capítulos en chino con su orden
def replace_chinese(match, counter=[1]):
    result = f'{match.group(1)}{counter[0]}{match.group(2)}'
    counter[0] += 1
    return result

# Aplicar reemplazos
english_modified = english_pattern.sub(replace_english, english_text)
chinese_modified = chinese_pattern.sub(replace_chinese, chinese_text)

# Guardar resultados
with open('issth_en_post.txt', 'w', encoding='utf-8') as f:
    f.write(english_modified)

with open('issth_ch_post.txt', 'w', encoding='utf-8') as f:
    f.write(chinese_modified)

print("Archivos generados: 'issth_en_post.txt' y 'issth_ch_post.txt'")
