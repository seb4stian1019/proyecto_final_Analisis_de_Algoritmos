# 5. Requerimiento 1: análisis de similitud textual

La aplicación permite elegir dos o más artículos del corpus y compara cada par de abstracts con seis algoritmos: cuatro clásicos programados desde cero y dos basados en modelos de inteligencia artificial. Todas las medidas se expresan entre 0 (nada en común) y 1 (textos iguales o vectores en la misma dirección).

## 5.1 Preprocesamiento

Antes de comparar, cada abstract se convierte en una lista de palabras (función `preprocesar` de `similitud.py`):

1. Se pasa a minúsculas.
2. Se separa en palabras formadas solo por letras; los números y los signos se descartan.
3. Se eliminan las palabras vacías del inglés (artículos, preposiciones, pronombres; 121 palabras escritas en el código) y las de una sola letra.

Los algoritmos clásicos comparan estas listas de palabras y no letra por letra. Así la comparación refleja los temas compartidos, y las matrices de programación dinámica quedan de unas 115 × 97 casillas en lugar de 1.379 × 1.088 caracteres. El modelo MiniLM, en cambio, recibe el abstract original, porque fue entrenado con texto natural completo.

## 5.2 Algoritmos clásicos

**Distancia de Levenshtein (programación dinámica).** Es el mínimo número de operaciones (insertar, borrar o sustituir una palabra) para convertir un texto en el otro. Se llena una matriz D de (n + 1) × (m + 1), donde D[i][j] es la distancia entre las primeras i palabras de A y las primeras j de B:

```latex
D[i][0] = i,\quad D[0][j] = j,\quad
D[i][j] = \begin{cases} D[i-1][j-1] & \text{si } a_i = b_j \\ 1 + \min(D[i-1][j],\ D[i][j-1],\ D[i-1][j-1]) & \text{si no} \end{cases}
```

La similitud es 1 − D[n][m] / max(n, m). Costo: O(n·m) en tiempo y en memoria.

**Subsecuencia común más larga, LCS (programación dinámica).** Es la secuencia más larga de palabras que aparece en ambos textos en el mismo orden, aunque no sea continua:

```latex
L[i][0] = L[0][j] = 0,\quad
L[i][j] = \begin{cases} L[i-1][j-1] + 1 & \text{si } a_i = b_j \\ \max(L[i-1][j],\ L[i][j-1]) & \text{si no} \end{cases}
```

La similitud es L[n][m] / max(n, m). Recorriendo la matriz desde la esquina final hacia atrás se recuperan las palabras de la subsecuencia. Costo: O(n·m).

**Coeficiente de Jaccard (conjuntos).** Compara los conjuntos de palabras distintas, sin importar el orden ni las repeticiones: J(A, B) = |A ∩ B| / |A ∪ B|. Costo: O(n + m) en promedio, porque los conjuntos de Python son tablas hash.

**Similitud del coseno con TF-IDF (espacio vectorial).** Cada abstract se representa como un vector con un peso por palabra:

```latex
\text{tf}(t, d) = \frac{\text{veces que } t \text{ aparece en } d}{\text{palabras de } d},\quad
\text{idf}(t) = \ln\frac{N}{\text{df}(t)},\quad
w(t, d) = \text{tf}(t, d)\cdot\text{idf}(t)
```

N = 20 es el número de abstracts y df(t) es en cuántos aparece la palabra t. Una palabra presente en los 20 abstracts tiene idf = ln(1) = 0 y no aporta; una palabra rara pesa más. El idf se calcula una sola vez con todo el corpus, para que el peso de cada palabra no dependa de qué artículos elija el usuario. La similitud es el coseno del ángulo entre los dos vectores:

```latex
\cos\theta = \frac{u \cdot v}{\lVert u \rVert\,\lVert v \rVert}
```

Costo: O(N·n) para el idf (una vez) y O(n + m) por par.

## 5.3 Modelos basados en inteligencia artificial

El enunciado permite usar modelos preentrenados para vectorizar los abstracts. En ambos casos el modelo solo produce el vector; el coseno se calcula a mano con la función `coseno_listas`.

- **GloVe** (Pennington et al., 2014), 50 dimensiones. Es un diccionario fijo que asigna a cada palabra un vector aprendido de Wikipedia. El vector del abstract es el promedio, calculado en el proyecto, de los vectores de sus palabras. No tiene en cuenta el orden ni el contexto.
- **all-MiniLM-L6-v2** (Sentence-BERT; Reimers y Gurevych, 2019), 384 dimensiones. Es una red neuronal tipo transformer que lee el abstract completo y produce un único vector, teniendo en cuenta el contexto de cada palabra.

Los vectores de los 20 abstracts se calculan una vez (`req1_embeddings.py`) y se guardan en `resultados/req1_embeddings.json`.

## 5.4 Caso de estudio: artículos 11 y 16

Se eligieron los artículos 11 («A scoping review on how generative artificial intelligence transforms assessment in higher education») y 16 («Generative Artificial Intelligence in Tertiary Education: Assessment Redesign Principles and Considerations»). Ambos tratan el mismo tema, el impacto de la IA generativa en la evaluación universitaria, pero con vocabulario distinto («higher education» frente a «tertiary education»). Después del preprocesamiento tienen 115 y 97 palabras.

### 5.4.1 Levenshtein

Para mostrar el llenado completo de la matriz se usa la primera oración de cada abstract. La tabla muestra D[i][j].

| | ∅ | emergence | generative | artificial | intelligence | ai | chatgpt | sparked | significant | assessment | concerns | within | tertiary | education |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ∅ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
| generative | 1 | 1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| artificial | 2 | 2 | 2 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| intelligence | 3 | 3 | 3 | 2 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| provides | 4 | 4 | 4 | 3 | 2 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| opportunities | 5 | 5 | 5 | 4 | 3 | 3 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| challenges | 6 | 6 | 6 | 5 | 4 | 4 | 4 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| higher | 7 | 7 | 7 | 6 | 5 | 5 | 5 | 5 | 5 | 6 | 7 | 8 | 9 | 10 |
| education | 8 | 8 | 8 | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 7 | 8 | 9 | 9 |

La distancia de las dos oraciones es D[8][13] = 9. La diagonal que baja por «generative», «artificial» e «intelligence» no suma operaciones, porque esas palabras coinciden en el mismo orden. Con los abstracts completos la distancia es 109, y la similitud es 1 − 109/115 = 0,0522.

### 5.4.2 LCS

| | ∅ | emergence | generative | artificial | intelligence | ai | chatgpt | sparked | significant | assessment | concerns | within | tertiary | education |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ∅ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| generative | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| artificial | 0 | 0 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| intelligence | 0 | 0 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| provides | 0 | 0 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| opportunities | 0 | 0 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| challenges | 0 | 0 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| higher | 0 | 0 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| education | 0 | 0 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 |

La subsecuencia común de las dos oraciones es «generative artificial intelligence education» (4 palabras). Con los abstracts completos tiene 11 palabras («generative artificial intelligence education assessment generative retrieved education assessment ai ai»), y la similitud es 11/115 = 0,0957.

### 5.4.3 Jaccard

El artículo 11 tiene |A| = 82 palabras distintas y el 16, |B| = 72. Comparten 12: ai, artificial, assessment, challenges, education, generative, integrity, intelligence, provide, rethink, retrieved, students. La unión tiene 142 palabras, así que J = 12/142 = 0,0845.

### 5.4.4 Coseno con TF-IDF

Solo las palabras comunes aportan al producto punto. La tabla las ordena por su aporte.

| Palabra | Veces en 11 | Veces en 16 | df | idf | Peso en 11 | Peso en 16 | Producto |
|---|---|---|---|---|---|---|---|
| generative | 2 | 7 | 5 | 1,3863 | 0,02411 | 0,10004 | 0,002412 |
| assessment | 8 | 3 | 10 | 0,6931 | 0,04822 | 0,02144 | 0,001034 |
| integrity | 1 | 1 | 2 | 2,3026 | 0,02002 | 0,02374 | 0,000475 |
| rethink | 1 | 1 | 2 | 2,3026 | 0,02002 | 0,02374 | 0,000475 |
| retrieved | 1 | 1 | 2 | 2,3026 | 0,02002 | 0,02374 | 0,000475 |
| students | 2 | 1 | 8 | 0,9163 | 0,01594 | 0,00945 | 0,000151 |
| challenges | 1 | 1 | 6 | 1,2040 | 0,01047 | 0,01241 | 0,000130 |
| provide | 1 | 1 | 10 | 0,6931 | 0,00603 | 0,00715 | 0,000043 |
| ai | 2 | 7 | 18 | 0,1054 | 0,00183 | 0,00760 | 0,000014 |
| education | 4 | 2 | 18 | 0,1054 | 0,00366 | 0,00217 | 0,000008 |
| artificial | 2 | 1 | 20 | 0,0000 | 0,00000 | 0,00000 | 0,000000 |
| intelligence | 2 | 1 | 20 | 0,0000 | 0,00000 | 0,00000 | 0,000000 |

u · v = 0,005217, |u| = 0,19673 y |v| = 0,26970. Entonces cos θ = 0,005217 / (0,19673 · 0,26970) = 0,0983, un ángulo de 84,4°. «artificial» e «intelligence» están en los 20 abstracts y su idf es 0; «generative» aporta casi la mitad del producto porque aparece en solo 5 abstracts.

### 5.4.5 Modelos de IA

| Modelo | Dimensiones | u · v | ‖u‖ | ‖v‖ | Coseno | Ángulo |
|---|---|---|---|---|---|---|
| GloVe | 50 | 8,3862 | 3,2532 | 2,7041 | 0,9533 | 17,6° |
| MiniLM | 384 | 0,7355 | 1,0000 | 1,0000 | 0,7355 | 42,7° |

### 5.4.6 Resumen del caso

La figura `resultados/req1_grafico_caso.png` muestra los seis valores. La columna «Puesto» indica en qué lugar queda el artículo 16 cuando se ordenan los 19 artículos restantes según su similitud con el 11 (1 = el más parecido).

| Algoritmo | Similitud 11-16 | Puesto del 16 |
|---|---|---|
| Levenshtein | 0,0522 | 6 de 19 |
| LCS | 0,0957 | 7 de 19 |
| Jaccard | 0,0845 | 16 de 19 |
| Coseno TF-IDF | 0,0983 | 1 de 19 |
| GloVe | 0,9533 | 17 de 19 |
| MiniLM | 0,7355 | 1 de 19 |

## 5.5 Resultados en todo el corpus

Con los 20 abstracts se calcularon las 190 comparaciones posibles para cada algoritmo (`resultados/req1_matriz_*.csv`).

| Algoritmo | Promedio | Mínimo | Máximo | Par más parecido |
|---|---|---|---|---|
| Levenshtein | 0,0413 | 0,0084 | 0,1092 | 2-20 |
| LCS | 0,0889 | 0,0327 | 0,1727 | 2-9 |
| Jaccard | 0,0908 | 0,0268 | 0,1607 | 8-10 |
| Coseno TF-IDF | 0,0432 | 0,0010 | 0,1984 | 2-6 |
| GloVe | 0,9683 | 0,9388 | 0,9903 | 15-20 |
| MiniLM | 0,5532 | 0,3406 | 0,8098 | 6-9 |

## 5.6 Análisis crítico

**Qué mide cada algoritmo.** Los seis algoritmos no miden lo mismo, y por eso sus valores no se comparan directamente: lo comparable es el orden en que ponen a los artículos. Levenshtein y LCS miden coincidencia de palabras en el mismo orden; Jaccard, vocabulario compartido; TF-IDF, vocabulario compartido pesado por su rareza; GloVe y MiniLM, cercanía de significado.

**Algoritmos de orden (Levenshtein y LCS).** Dan valores muy bajos (0,0522 y 0,0957) y ponen al artículo 16 en los puestos 6 y 7. Dos abstracts escritos por autores distintos casi nunca repiten frases en el mismo orden: de 115 palabras, la subsecuencia común solo tiene 11. Sirven para detectar textos copiados o parafraseados de cerca, no para comparar temas.

**Jaccard.** Pone al 16 en el puesto 16 de 19, casi al final. Cuenta igual una palabra rara y una común, y no reconoce variantes: «provides» y «provide» o «higher» y «tertiary» cuentan como palabras distintas. Como los 20 abstracts son del mismo campo, todos comparten palabras generales y Jaccard no logra separarlos.

**TF-IDF.** Es el mejor de los clásicos en este caso: pone al 16 en el puesto 1. El idf anula las palabras que están en todos los abstracts («artificial», «intelligence») y da peso a las que solo comparten pocos («generative», «integrity», «retrieved»). Aun así, su valor absoluto es bajo (0,0983), porque solo cuenta palabras idénticas.

**GloVe.** Da valores muy altos para todos los pares (entre 0,9388 y 0,9903) y pone al 16 en el puesto 17. Al promediar entre 70 y 150 vectores de palabras, cada abstract se acerca a un vector de «inglés académico general», y las diferencias de tema se diluyen. Es la limitación conocida de promediar embeddings de palabras: se pierde el orden y el contexto.

**MiniLM.** Es el que mejor refleja el parecido de tema: 0,7355 (ángulo de 42,7°) y el puesto 1 para el artículo 16. Sus valores se reparten en un rango útil (de 0,3406 a 0,8098 en el corpus) y no depende de que los dos abstracts usen las mismas palabras, porque representa el texto completo teniendo en cuenta el contexto de cada palabra.

**Conclusión del caso.** El único algoritmo clásico que coincide con MiniLM en señalar al artículo 16 como el más parecido al 11 es TF-IDF. Los clásicos son transparentes y cada paso se puede verificar a mano, pero dependen de que los textos usen las mismas palabras. MiniLM captura el significado aunque cambien las palabras, a cambio de ser una caja negra de 22 millones de parámetros que no se puede seguir paso a paso. Para comparar temas en este corpus, la mejor opción es MiniLM, y entre los clásicos, TF-IDF.

## 5.7 Complejidad

| Algoritmo | Tiempo por par | Memoria |
|---|---|---|
| Levenshtein | O(n·m) | O(n·m) |
| LCS | O(n·m) (+ O(n + m) para reconstruir) | O(n·m) |
| Jaccard | O(n + m) en promedio | O(n + m) |
| Coseno TF-IDF | O(n + m) (+ O(N·n) una vez para el idf) | O(n + m) |
| GloVe + coseno | O(d) con d = 50 (+ O(n·d) una vez para promediar) | O(d) |
| MiniLM + coseno | O(d) con d = 384 (el modelo se ejecuta una vez por abstract) | O(d) |

n y m: palabras de cada abstract; N: abstracts del corpus; d: dimensiones del vector.
