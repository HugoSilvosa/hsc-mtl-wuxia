# Wuxia Corpus

Tools for automatic processing and alignment of Chinese-English wuxia novels.

## Description

This project processes and aligns chapters of Chinese-English wuxia novels using multilingual embeddings (LaBSE) and dynamic programming. It includes scripts for preprocessing, alignment, and similarity analysis.

## Datasets

| Dataset           | Novels                        | Chapters      | Description                                  |
| ----------------- | ----------------------------- | ------------- | ------------------------------------------- |
| **AWE**     | A Will Eternal                | ~1300         | Wuxia novel with Chinese-English translation |
| **CONDOR**  | The Condor Trilogy (Jin Yong) | 3 parts       | Complete trilogy in 3 volumes                |
| **GU**      | Reverend Insanity              | ~350k segments| Wuxia novel collection                      |
| **ISSTH**   | I Shall Seal the Heavens       | ~900+         | Wuxia/Xianxia novel                           |

## Project Structure

```
wuxia_corpus/
├── src/
│   ├── __init__.py
│   ├── preprocessing/
│   │   ├── chinese.py    # Chapter segmentation in Chinese
│   │   └── english.py    # Chapter segmentation in English
│   ├── alignment/
│   │   ├── final_awe.py  # AWE alignment with LaBSE
│   │   ├── final_gu.py   # GU alignment with LaBSE
│   │   ├── final_condor.py # CONDOR alignment
│   │   └── codigo.py     # Additional alignment code
│   ├── analysis/
│   │   └── similitudes.py # Cosine similarity calculation
│   └── common/
│       ├── config_loader.py  # YAML configuration loading
│       ├── utils.py          # Shared utilities
│       └── pdf_reader.py     # PDF reader
├── data/
│   ├── <novela>/
│   │   ├── raw/        # Original unprocessed text
│   │   ├── segmented/  # Divided chapters
│   │   │   └── chapter/ # ch*.txt and en*.txt files
│   │   └── processed/  # Aligned results (final_*.txt)
│   └── *.txt           # Pre-generated embedding files
└── stats.txt           # Processing statistics
```

## Usage

### 1. Preprocessing (Chapter Division)

**Chinese:**

```bash
python -m src.preprocessing.chinese --novela awe --input awe_ch.txt --outname segmented/chapter
python -m src.preprocessing.chinese --novela condor --input chinese_condor_1.txt --outname segmented/chapter
python -m src.preprocessing.chinese --novela gu --input guzhenren_ch.txt --outname segmented/chapter
```

**English:**

```bash
python -m src.preprocessing.english --novela awe --input awe_en.txt --outname segmented/chapter
python -m src.preprocessing.english --novela condor --input english_condor_1.txt --outname segmented/chapter
python -m src.preprocessing.english --novela gu --input guzhenren_en.txt --outname segmented/chapter
```

### 2. Alignment (Chinese-English Alignment)

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

### 3. Similarity Analysis

```bash
python -m src.analysis.similitudes
```

## Alignment Algorithm

The alignment uses LaBSE embeddings with dynamic programming considering:

- **1-1**: 1 Chinese segment : 1 English segment
- **1-2**: 1 Chinese segment : 2 English segments
- **2-1**: 2 Chinese segments : 1 English segment
- **1-3, 3-1**: 3-multi segment alignments
- **1-4, 4-1**: 4-multi segment alignments
- **Skips**: Penalty (`skip_penalty`) for unaligned segments

## Results (Statistics)

| Corpus      | Time (s) | Chinese Seg. | English Seg. | Aligned Pairs |
| ----------- | -------- | ------------ | ------------ | ------------- |
| GU (Total)  | 5518.62  | 352,097      | 334,606      | 325,032       |
| AWE (Total) | 2745.79  | 77,232       | 153,754      | 76,678        |
| CONDOR (Total) | 2899.62 | 128,500      | 182,646      | 123,033       |

## External Tools

- **Vecalign**: Linear sentence alignment (see `aligners/vecalign/README.md`)
- **Bertalign**: BERT-based alignment (see `aligners/bertalign/`)

## Output

Processed files generate:

- `final_*.txt`: Aligned pairs in format `chinese ; english`
- `final_*_similitudes.txt`: Similarity scores for each pair
- `final_*_stats.txt`: Alignment statistics