import re
import html
from tqdm import tqdm
import pdfplumber
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)
class CorpusBuilder:
    """
    Construye un corpus alineado línea a línea a partir de dos archivos:
    uno en inglés y otro en chino (en formato .txt).
    Si el archivo en inglés está en PDF, se puede convertir a TXT usando
    el método pdf_to_txt() y luego usar la ruta resultante.
    """

    def __init__(self, english_txt_path, chinese_txt_path):
        self.english_txt_path = english_txt_path
        self.chinese_txt_path = chinese_txt_path
        self.english_lines = []
        self.chinese_lines = []

    # -------------------------------------------------------------------------
    #   1. Métodos relacionados con PDF -> TXT
    # -------------------------------------------------------------------------
    @staticmethod
    def agrupar_palabras_en_lineas(palabras, tolerancia_y=5):
        """
        Acomoda las 'palabras' (o fragmentos) extraídos de una página PDF en 'líneas',
        basándose en la coordenada vertical (top).
        """
        # Ordenar por posición vertical y luego horizontal
        palabras_ordenadas = sorted(palabras, key=lambda w: (w['top'], w['x0']))
        lineas = []
        linea_actual = []
        current_top = None

        for palabra in palabras_ordenadas:
            if current_top is None:
                current_top = palabra['top']
                linea_actual.append(palabra)
            elif abs(palabra['top'] - current_top) <= tolerancia_y:
                linea_actual.append(palabra)
            else:
                lineas.append(linea_actual)
                linea_actual = [palabra]
                current_top = palabra['top']

        if linea_actual:
            lineas.append(linea_actual)

        return lineas

    @staticmethod
    def unir_lineas_en_parrafos(lineas, separacion_vertical_umbral=10):
        """
        Une líneas en párrafos basándose en la distancia vertical entre líneas
        (si hay un espacio mayor que `separacion_vertical_umbral`, se asume un nuevo párrafo).
        """
        parrafos = []
        parrafo_actual = []
        prev_bottom = None

        for linea in lineas:
            # Ordenar la línea por coordenada x para asegurarse
            texto_linea = " ".join(p['text'] for p in sorted(linea, key=lambda w: w['x0']))

            top_linea = min(p['top'] for p in linea)
            bottom_linea = max(p['bottom'] for p in linea)
            
            if prev_bottom is not None:
                # Si la separación vertical es grande, se asume nuevo párrafo
                if (top_linea - prev_bottom) > separacion_vertical_umbral:
                    parrafos.append(" ".join(parrafo_actual))
                    parrafo_actual = [texto_linea]
                else:
                    parrafo_actual.append(texto_linea)
            else:
                parrafo_actual.append(texto_linea)

            prev_bottom = bottom_linea

        if parrafo_actual:
            parrafos.append(" ".join(parrafo_actual))

        return parrafos



    def pdf_to_txt(self, ruta_pdf, ruta_txt):
        """
        Convierte un PDF a texto plano agrupando palabras en líneas y luego en párrafos.
        Aplica limpieza básica y guarda el resultado en un archivo .txt.
        """
        print(f"Convirtiendo PDF '{ruta_pdf}' a TXT '{ruta_txt}' ...")

        todos_parrafos = []
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in tqdm(pdf.pages, desc="Procesando páginas PDF"):
                palabras = pagina.extract_words()
                if not palabras:
                    continue
                lineas = self.agrupar_palabras_en_lineas(palabras, tolerancia_y=5)
                parrafos = self.unir_lineas_en_parrafos(lineas, separacion_vertical_umbral=10)
                todos_parrafos.extend(parrafos)

        # Unir párrafos cortados por salto de página
        parrafos_limpios = []
        i = 0
        while i < len(todos_parrafos):
            actual = todos_parrafos[i].strip()
            while (
                i < len(todos_parrafos) - 1
                and actual
                and actual[-1] not in ".!?"
                and todos_parrafos[i + 1].strip()
                and todos_parrafos[i + 1].strip()[0].islower()
            ):
                actual += " " + todos_parrafos[i + 1].strip()
                i += 1
            parrafos_limpios.append(actual)
            i += 1

        # Filtrado final: eliminar capítulos repetidos y líneas de Translator/Editor
        parrafos_finales = []
        prev_chapter = None
        for parrafo in parrafos_limpios:
            p = parrafo.strip()

            if re.search(r'\bTranslator\b|\bEditor\b', p, re.IGNORECASE):
                continue

            if p.startswith("Chapter"):
                if p == prev_chapter:
                    continue
                prev_chapter = p

            parrafos_finales.append(p)

        with open(ruta_txt, "w", encoding="utf-8") as f:
            for parrafo in parrafos_finales:
                f.write(parrafo + "\n")

        print(f"Conversión completada. El archivo de texto limpio se ha guardado como '{ruta_txt}'.")


    # -------------------------------------------------------------------------
    #   2. Procesamiento y limpieza de TXT para construir el corpus
    # -------------------------------------------------------------------------
    def clean_line(self, line):
        line = line.strip()

        # 1. Eliminar líneas completamente entre paréntesis (normales o chinos)
        if re.fullmatch(r'[\(（][^()（）]{0,1000}[\)）]', line):
            return ''

        # 2. Eliminar paréntesis con solo un número (occidentales y chinos)
        line = re.sub(r'[\(（]\d+[\)）]', '', line)

        # 3. Eliminar paréntesis (normales o chinos) al inicio tipo: (18) texto ó （18）texto
        line = re.sub(r'^[\(（]\d+[\)）]\s*', '', line)

        # 4. Eliminar referencias a translator/editor
        if re.search(r'(translator|editor)\s*[:：]', line, re.IGNORECASE):
            return ''

        # 5. Desescape doble
        line = html.unescape(html.unescape(line))

        # 6. Eliminar & remanente
        line = line.replace('&', '')

        # 7. Limpiar comillas, llaves, punto y coma
        line = re.sub(r'[{}]', '', line)
        line = re.sub(r'[“”"\'«»]', '', line)
        line = re.sub(r';', '', line)

        return line.strip()



    def is_ellipsis_line(self, line):
        line = line.strip()
        return not line or bool(re.fullmatch(r'[\.\?!…。！？？]+', line))

    def remove_redundant_duplicates(self, lines):
        cleaned = []
        i = 0
        while i < len(lines):
            if i + 2 < len(lines):
                merged = re.sub(r'\s+', '', lines[i] + lines[i+1])
                third = re.sub(r'\s+', '', lines[i+2])
                if merged == third:
                    cleaned.append(lines[i].strip() + " " + lines[i+1].strip())
                    i += 3
                    continue
            cleaned.append(lines[i].strip())
            i += 1
        return cleaned

    def parse_txt_file(self, path, lang="english"):
        print(f"Leyendo y limpiando TXT en {lang}...")
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned = []
        for line in tqdm(lines, desc=f"Procesando líneas TXT ({lang})"):
            cl = self.clean_line(line)
            if cl and not self.is_ellipsis_line(cl):
                cleaned.append(cl)

        return cleaned
    def align_by_char_balance(self, tolerance=0.3):
        """
        Alinea bloques entre inglés y chino acumulando líneas hasta que las longitudes (en caracteres)
        estén balanceadas dentro de una tolerancia.
        """
        aligned = []
        eng = self.english_lines
        chi = self.chinese_lines

        i = 0  # índice en inglés
        j = 0  # índice en chino

        while i < len(eng) and j < len(chi):
            eng_block = []
            chi_block = []
            eng_len = 0
            chi_len = 0

            # Acumular oraciones en inglés
            while i < len(eng) and eng_len < chi_len * (1 - tolerance):
                eng_block.append(eng[i])
                eng_len += len(eng[i])
                i += 1

            # Acumular líneas en chino
            while j < len(chi) and chi_len < eng_len * (1 - tolerance):
                chi_block.append(chi[j])
                chi_len += len(chi[j])
                j += 1

            # Asegurar al menos 1 línea de cada lado
            if not eng_block and i < len(eng):
                eng_block.append(eng[i])
                i += 1
            if not chi_block and j < len(chi):
                chi_block.append(chi[j])
                j += 1

            aligned.append((" ".join(eng_block), "".join(chi_block)))

        return aligned

    def build_corpus(self, output_path):
        self.english_lines = self.parse_txt_file(self.english_txt_path, lang="english")
        self.chinese_lines = self.parse_txt_file(self.chinese_txt_path, lang="chinese")

        print("Alineando bloques por balance de caracteres...")
        aligned = self.align_by_char_balance()

        print(f"Guardando corpus alineado con {len(aligned)} pares...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for eng, chi in aligned:
                f.write(f"{eng} ; {chi}\n")

        print(f"\nCorpus generado correctamente en: {output_path}")


# ------------------------------------------------------------------------------
# Ejemplo de uso
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # 1) Convertir un PDF de inglés a TXT
    builder = CorpusBuilder(None, None)  # De momento no pasamos rutas
    # builder.pdf_to_txt("guzhenren.pdf", "guzhenren_en.txt")
    # builder.pdf_to_txt("chapters/chapter/1en.pdf", "asdasd.txt")

    # 2) Ahora crear otro objeto con las rutas TXT (inglés y chino)
    parser = CorpusBuilder("2es.txt", "2ch.txt")
    parser.build_corpus("corpus.txt")

