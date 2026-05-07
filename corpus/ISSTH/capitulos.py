import re

# Cargar archivos
with open('issth_en_post.txt', 'r', encoding='utf-8') as f:
    english_text = f.read()

with open('issth_ch_post.txt', 'r', encoding='utf-8') as f:
    chinese_text = f.read()

# Expresiones regulares actualizadas para incluir el título completo
english_pattern = re.compile(r'(Chapter\s+\w+[^\n]*)', re.IGNORECASE)
chinese_pattern = re.compile(r'(第[\d一二三四五六七八九十百千万零]+[章节][^\n]*)')

# Encontrar capítulos completos con título
english_chapters = english_pattern.findall(english_text)
chinese_chapters = chinese_pattern.findall(chinese_text)

# Preparar salida
output_lines = []
output_lines.append(f'Capítulos en inglés encontrados: {len(english_chapters)}')
output_lines.append(f'Capítulos en chino encontrados: {len(chinese_chapters)}\n')
output_lines.append('Coincidencias por orden de aparición:\n')

min_len = min(len(english_chapters), len(chinese_chapters))

for i in range(min_len):
    output_lines.append(f'{i+1:03}: {english_chapters[i]}  <-->  {chinese_chapters[i]}')

# Guardar en archivo
with open('comparison_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Comparación guardada en 'comparison_output.txt'")
