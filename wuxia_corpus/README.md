# Wuxia Corpus

Herramientas para procesamiento y alineamiento automático de novelas wuxia en chino-inglés.

## Descripción

Este proyecto procesa y alinea capítulos de novelas wuxia chino-inglés usando embeddings multilingües (LaBSE) y programación dinámica. Incluye scripts para preprocesamiento, alineamiento y análisis de similitud.

## Datasets

| Dataset          | Novelas                       | Capítulos      | Descripción                               |
| ---------------- | ----------------------------- | --------------- | ------------------------------------------ |
| **AWE**    | A Will Eternal                | ~1300           | Novela wuxia con traducción chino-inglés |
| **CONDOR** | The Condor Trilogy (Jin Yong) | 3 partes        | Trilogía completa con 3 volúmenes        |
| **GU**     | Reverend Insanity             | ~350k segmentos | Colección de novelas wuxia                |
| **ISSTH**  | I Shall Seal the Heavens      | ~900+           | Novel wuxia/Xianxia                        |

## Estructura del Proyecto

```
wuxia_corpus/
├── src/
│   ├── __init__.py
│   ├── preprocessing/
│   │   ├── chinese.py    # Segmentación de capítulos en chino
│   │   └── english.py    # Segmentación de capítulos en inglés
│   ├── alignment/
│   │   ├── final_awe.py  # Alineamiento AWE con LaBSE
│   │   ├── final_gu.py   # Alineamiento GU con LaBSE
│   │   ├── final_condor.py # Alineamiento CONDOR
│   │   └── codigo.py     # Código adicional de alineamiento
│   ├── analysis/
│   │   └── similitudes.py # Cálculo de similitud coseno
│   └── common/
│       ├── config_loader.py  # Carga de configuración YAML
│       ├── utils.py          # Utilidades compartidas
│       └── pdf_reader.py     # Lectura de PDFs
├── data/
│   ├── <novela>/
│   │   ├── raw/        # Texto original sin procesar
│   │   ├── segmented/  # Capítulos divididos
│   │   │   └── chapter/ # Archivos ch*.txt y en*.txt
│   │   └── processed/  # Resultados alineados (final_*.txt)
│   └── *.txt           # Archivos de embeddings pre-generados
└── stats.txt           # Estadísticas de procesamiento
```

## Uso

### 1. Preprocesamiento (Dividir en capítulos)

**Chino:**

```bash
python -m src.preprocessing.chinese --novela awe --input awe_ch.txt --outname segmented/chapter
python -m src.preprocessing.chinese --novela condor --input chinese_condor_1.txt --outname segmented/chapter
python -m src.preprocessing.chinese --novela gu --input guzhenren_ch.txt --outname segmented/chapter
```

**Inglés:**

```bash
python -m src.preprocessing.english --novela awe --input awe_en.txt --outname segmented/chapter
python -m src.preprocessing.english --novela condor --input english_condor_1.txt --outname segmented/chapter
python -m src.preprocessing.english --novela gu --input guzhenren_en.txt --outname segmented/chapter
```

### 2. Alineamiento (Chinese-English Alignment)

**AWE:**

```bash
python -m src.alignment.final_awe
```

**GU:**

```bash
python -m src.alignment.final_gu
```

**CONDOR:**

```bash
python -m src.alignment.final_condor
```

### 3. Análisis de Similitud

```bash
python -m src.analysis.similitudes
```

## Algoritmo de Alineamiento

El alineamiento usa embeddings LaBSE con programación dinámica considerando:

- **1-1**: 1 segmento chino : 1 segmento inglés
- **1-2**: 1 segmento chino : 2 segmentos ingleses
- **2-1**: 2 segmentos chinos : 1 segmento inglés
- **1-3, 3-1**: Alineamientos 3-varios
- **1-4, 4-1**: Alineamientos 4-varios
- **Saltos**: Penalización (`skip_penalty`) para segmentos no alineados

## Resultados (Estadísticas)

| Corpus         | Tiempo (s) | Seg. Chinos | Seg. Ingleses | Pares Alineados |
| -------------- | ---------- | ----------- | ------------- | --------------- |
| GU (Total)     | 5518.62    | 352,097     | 334,606       | 325,032         |
| AWE (Total)    | 2745.79    | 77,232      | 153,754       | 76,678          |
| CONDOR (Total) | 2899.62    | 128,500     | 182,646       | 123,033         |

## Herramientas Externas

- **Vecalign**: Alineamiento de oraciones en tiempo lineal (ver `aligners/vecalign/README.md`)
- **Bertalign**: Alineamiento basado en BERT (ver `aligners/bertalign/`)

## Salida

Los archivos procesados generan:

- `final_*.txt`: Pares alineados en formato `chino ; inglés`
- `final_*_similitudes.txt`: Puntajes de similitud para cada par
- `final_*_stats.txt`: Estadísticas de alineamiento
