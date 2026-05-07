# Análisis Estadístico y Riqueza Léxica en la Traducción del Género Wuxia

Este apartado presenta el análisis cuantitativo de dos corpus paralelos (chino-inglés) centrados en la literatura fantástica china (Wuxia). El estudio contrasta un **Corpus Principal** (compuesto por novelas seleccionadas ad hoc) y un **Corpus de Referencia** (extraído del repositorio Hugging Face y unificado en sus particiones de *train, validation* y *test*), con el objetivo de evaluar las dinámicas lingüísticas subyacentes en el proceso de traducción.

---

## 1. Fundamentación Metodológica y Métricas de Análisis

Para garantizar la rigurosidad del análisis y mitigar los sesgos estadísticos derivados de la disparidad en la longitud de los textos, el estudio se apoya en las siguientes métricas de lingüística computacional:

* **Volumen del Corpus (Tokens y Types):** El recuento de *Tokens* cuantifica el volumen total de palabras (en el texto meta) o caracteres/palabras segmentadas (en el texto origen). Por su parte, los *Types* representan el vocabulario único, esto es, el inventario léxico real desplegado en la obra. La relación entre ambos es fundamental para establecer ratios de expansión.
* **TTR Clásico (Type-Token Ratio):** Constituye la medida base de la diversidad léxica ($TTR = \frac{Types}{Tokens} \times 100$). No obstante, presenta una limitación metodológica crítica en corpus extensos, dado que la adición natural de palabras funcionales tiende a reducir drásticamente este índice, invalidando su uso para comparativas globales en novelas.
* **STTR (Standardized TTR):** Corrige la desviación del TTR clásico fragmentando el texto en bloques estandarizados (en este estudio, 1.000 tokens), calculando la diversidad de cada bloque de forma independiente y extrayendo una media aritmética. Esta métrica permite la comparación asimétrica entre textos de longitudes dispares.
* **Índice Guiraud (R):** Opera como una compensación matemática frente a la extensión del texto ($R = \frac{Types}{\sqrt{Tokens}}$). Proporciona una medida estable de la "reserva de vocabulario" del autor o traductor, penalizando en menor medida la recurrencia de términos gramaticales.
* **MTLD (Measure of Textual Lexical Diversity):** Evalúa la diversidad léxica secuencial. Calcula la longitud media de un segmento de palabras antes de que su TTR interno decaiga por debajo del umbral estándar de 0.72. Valores superiores indican una mayor resistencia a la repetición léxica a lo largo del flujo narrativo.
* **VOCD-D (Aproximación HD-D):** Constituye el estándar contemporáneo para la evaluación probabilística de la complejidad léxica. Mediante un muestreo aleatorio reiterado (típicamente de 42 tokens), calcula la probabilidad de aparición de vocabulario único, reflejando la complejidad microestructural del texto en una escala de 0 a 1.
* **Densidad Léxica:** Cuantifica la proporción de palabras con carga semántica plena (sustantivos, verbos, adjetivos y adverbios) frente a las categorías gramaticales de carácter funcional. Su análisis es crucial para determinar si la traducción ha diluido la carga informativa original.
* **Hapax Legomena:** Contabiliza en términos absolutos y porcentuales los vocablos que registran una única ocurrencia en todo el corpus. En traductología, constituye un indicador primario de singularidad estilística, creatividad y, por contraposición, de los procesos de normalización durante la traducción.

---

## 2. Resultados Cuantitativos

A continuación, se exponen los datos brutos arrojados por el análisis computacional en ambos conjuntos de datos.

### 2.1. Corpus Principal (Novelas Seleccionadas)

**Texto Meta (Inglés):**
* **Tokens:** 9.351.283
* **Types:** 28.500
* **TTR Clásico:** 0.30%
* **STTR (Bloques 1k):** 39.97%
* **Índice Guiraud (R):** 9.32
* **MTLD:** 91.25
* **VOCD-D (HD-D):** 0.90
* **Densidad Léxica:** 63.81%
* **Hapax Legomena:** 5.161 (18.11% del vocabulario único)

**Texto Origen (Chino):**
* **Tokens:** 6.938.915
* **Types:** 133.374
* **TTR Clásico:** 1.92%
* **STTR (Bloques 1k):** 53.53%
* **Índice Guiraud (R):** 50.63
* **MTLD:** 168.60
* **VOCD-D (HD-D):** 0.93
* **Densidad Léxica:** 57.58%
* **Hapax Legomena:** 44.774 (33.57% del vocabulario único)

### 2.2. Corpus de Referencia (Dataset Hugging Face)

**Texto Meta (Inglés):**
* **Tokens:** 3.687.379
* **Types:** 23.657
* **TTR Clásico:** 0.64%
* **STTR (Bloques 1k):** 51.62%
* **Índice Guiraud (R):** 12.32
* **MTLD:** 178.98
* **VOCD-D (HD-D):** 0.90
* **Densidad Léxica:** 59.85%
* **Hapax Legomena:** 5.125 (21.66% del vocabulario único)

**Texto Origen (Chino):**
* **Tokens:** 2.741.077
* **Types:** 95.208
* **TTR Clásico:** 3.47%
* **STTR (Bloques 1k):** 67.43%
* **Índice Guiraud (R):** 57.51
* **MTLD:** 590.60
* **VOCD-D (HD-D):** 0.93
* **Densidad Léxica:** 60.06%
* **Hapax Legomena:** 36.949 (38.81% del vocabulario único)

---

## 3. Discusión de los Resultados y Análisis Comparativo

La sistematización de las métricas clave (véase la Tabla 1) facilita la identificación de patrones traductológicos transversales a ambos corpus.

**Tabla 1. Comparativa de las métricas clave de riqueza léxica.**
| Métrica | Principal (ZH) | Principal (EN) | Ref. HF (ZH) | Ref. HF (EN) |
| :--- | :--- | :--- | :--- | :--- |
| **STTR (1k)** | 53.53% | 39.97% | 67.43% | 51.62% |
| **Índice Guiraud** | 50.63 | 9.32 | 57.51 | 12.32 |
| **MTLD** | 168.60 | 91.25 | 590.60 | 178.98 |
| **Densidad Léxica** | 57.58% | 63.81% | 60.06% | 59.85% |
| **Hapax Legomena**| 33.57% | 18.11% | 38.81% | 21.66% |

### 3.1. Ratio de Expansión y Verbosidad Estructural
El análisis del volumen de tokens confirma una divergencia estructural predecible entre los sistemas lingüísticos. En el Corpus Principal, el idioma meta requiere un ratio de expansión de **1.35** (9,35M frente a 6,93M de tokens). Paralelamente, el Corpus de Referencia arroja un ratio virtualmente idéntico de **1.34**. Esta constante constata empíricamente que la traslación de la literatura Wuxia del chino (lengua aislante y altamente sintética) al inglés (lengua analítica) demanda una expansión del texto de aproximadamente un 35%, necesaria para acomodar elementos morfosintácticos inexistentes en el original.

### 3.2. Simplificación Léxica y Efecto de Normalización
El fenómeno traductológico más destacable reside en la asimetría del *Hapax Legomena*. En el texto origen, entre el 33.57% y el 38.81% de los *types* constituyen vocablos de aparición única, un indicador claro de la idiosincrasia descriptiva del género y la profusión de *Chengyu* (fraseologismos de cuatro caracteres). 

En el texto meta, esta proporción sufre una reducción drástica, situándose entre el 18.11% y el 21.66%. Este desplome certifica la existencia de un **proceso de normalización** durante la traducción. Los términos periféricos, poéticos o culturalmente opacos del chino son sustituidos e iterados mediante combinaciones de unidades léxicas inglesas de alta frecuencia, mitigando la singularidad del texto original.

### 3.3. Contracción de la Diversidad Secuencial
La normalización descrita se ve corroborada por los índices de diversidad estandarizada. El **Índice Guiraud** revela que el texto origen ostenta una reserva léxica proporcionalmente cinco veces superior a la de su traducción (50.63 frente a 9.32 en el Corpus Principal). Del mismo modo, el **MTLD** evidencia una contracción en la fluidez creativa: mientras que el autor original es capaz de encadenar largas secuencias (168.60 y 590.60 palabras) introduciendo constante novedad léxica, la traducción se ve forzada a reciclar vocabulario de manera mucho más prematura (a las 91.25 y 178.98 palabras, respectivamente).

### 3.4. Conservación de la Carga Informativa
Pese al evidente aplanamiento de la diversidad del vocabulario y a la inyección de millones de tokens funcionales fruto de la expansión estructural, la **Densidad Léxica** demuestra una notable resiliencia. En el Corpus de Referencia existe un equilibrio casi perfecto (60.06% ZH frente a 59.85% EN), mientras que en el Corpus Principal el texto meta logra incluso superar al original (63.81% EN frente a 57.58% ZH). 

Estos datos sugieren una aplicación exitosa de técnicas de compensación, tales como la sustantivación y la adjetivación compuesta. Como resultado, la traducción logra preservar la "densidad de la acción" por unidad de lectura, garantizando la conservación del ritmo narrativo vertiginoso que caracteriza a la literatura de artes marciales chinas.