# 6. Requerimiento 2: agrupamiento jerárquico

El objetivo es construir un árbol (dendrograma) que muestre qué abstracts se parecen entre sí. El proceso tiene cinco etapas: preprocesar cada abstract, calcular la similitud entre todos los pares, agrupar con tres criterios distintos programados desde cero, dibujar un dendrograma por criterio y evaluar cuál agrupa mejor con una métrica interna. Todo el código está en `clustering.py`; scipy solo se usa en `pruebas_clustering.py` para comprobar los resultados y no forma parte del proyecto.

## 6.1 Preprocesamiento y matriz de distancias

Se reutilizan las funciones del Requerimiento 1 (`similitud.py`): cada abstract se pasa a minúsculas, se separa en palabras formadas solo por letras y se eliminan las palabras vacías (sección 5.1). Luego cada abstract se representa como un vector TF-IDF, con el idf calculado sobre los 20 abstracts, y se compara con el coseno (sección 5.2). Se eligió el coseno con TF-IDF porque en el Requerimiento 1 fue el algoritmo clásico que ubicó en primer lugar al par 11-16, que trata el mismo tema.

El agrupamiento trabaja con distancias, así que la similitud se convierte en:

```latex
d(i, j) = 1 - \cos\theta_{ij}
```

La distancia vale 0 cuando dos abstracts tienen el mismo vocabulario con los mismos pesos y 1 cuando no comparten ninguna palabra con idf mayor que cero. El resultado es una matriz simétrica de 20 × 20 (`resultados/req2_distancias.csv`). Sus 190 distancias van de 0,8016 (artículos 2 y 6) a 0,9990, con promedio 0,9568: los 20 artículos tratan de IA en educación y comparten el vocabulario general, de modo que lo que los distingue son unas pocas palabras específicas.

## 6.2 Algoritmo aglomerativo

Los tres criterios siguen el mismo algoritmo (función `agrupar`):

1. Cada abstract empieza como un grupo propio: 20 grupos.
2. Se busca el par de grupos con la menor distancia y se unen en un grupo nuevo. La distancia a la que se unen es la altura de esa unión en el dendrograma.
3. Se calcula la distancia del grupo nuevo a cada uno de los demás grupos.
4. Se repite hasta que queda un solo grupo. Con 20 abstracts hay 19 uniones.

Los grupos se numeran como en la literatura: 0 a 19 son los abstracts (las hojas) y la unión número k crea el grupo 20 + k. La lista de uniones (grupo a, grupo b, altura, tamaño) es el árbol completo y se guarda en `resultados/req2_uniones_<criterio>.csv`.

## 6.3 Los tres criterios

Lo único que cambia entre criterios es el paso 3: cómo se mide la distancia entre el grupo nuevo A ∪ B y otro grupo X.

| Criterio | Definición | Fórmula de actualización |
|---|---|---|
| Single linkage (enlace simple) | Distancia entre los dos puntos más cercanos de los grupos | d(A ∪ B, X) = mín(d(A, X), d(B, X)) |
| Complete linkage (enlace completo) | Distancia entre los dos puntos más lejanos | d(A ∪ B, X) = máx(d(A, X), d(B, X)) |
| Average linkage (enlace promedio) | Promedio de todas las distancias entre puntos de los dos grupos | d(A ∪ B, X) = (\|A\|·d(A, X) + \|B\|·d(B, X)) / (\|A\| + \|B\|) |

Las fórmulas de la tercera columna dan exactamente el mismo valor que recorrer todos los pares de puntos, pero en tiempo constante, porque el mínimo (o máximo) de la unión es el mínimo (o máximo) de los dos mínimos, y el promedio de la unión es el promedio de los dos promedios ponderado por el número de pares. `pruebas_clustering.py` lo comprueba en 2.000 matrices aleatorias comparando contra una versión lenta que sí recorre todos los pares.

**Complejidad.** Hay n − 1 uniones. En cada una se busca el par más cercano entre k grupos activos, O(k²), y se actualizan k distancias, O(k). El total es Σ k(k − 1)/2 = O(n³) en tiempo y O(n²) en memoria por la matriz. Con n = 20 se revisan 1.330 pares en total.

## 6.4 Métrica de evaluación: correlación cofenética

La distancia cofenética c(i, j) es la altura del dendrograma a la que los abstracts i y j quedan por primera vez en el mismo grupo. Es la distancia que el árbol "dice" que hay entre ellos. El coeficiente de correlación cofenética es la correlación de Pearson entre las distancias originales y las cofenéticas, sobre los 190 pares i < j:

```latex
r = \frac{\sum_{i<j} (d_{ij} - \bar{d})(c_{ij} - \bar{c})}{\sqrt{\sum_{i<j} (d_{ij} - \bar{d})^2 \cdot \sum_{i<j} (c_{ij} - \bar{c})^2}}
```

Un valor cercano a 1 significa que el dendrograma conserva bien las distancias reales entre los abstracts. Es una métrica interna porque solo usa los datos y el árbol, sin etiquetas externas. Se calcula a mano en `matriz_cofenetica` (O(n²)) y `correlacion_cofenetica` (O(n²)).

## 6.5 Caso de estudio: artículos 2, 6, 11, 16 y 19

Para mostrar el algoritmo paso a paso se toman cinco artículos (`req2_caso_estudio.py`). El 2 y el 6 son el par más cercano del corpus, el 11 y el 16 son los del caso de estudio del Requerimiento 1, y con el 19 los tres criterios toman decisiones distintas en el tercer paso. Las distancias salen de la matriz de 20 × 20.

| | 2 | 6 | 11 | 16 | 19 |
|---|---|---|---|---|---|
| 2 | 0 | 0,8016 | 0,9142 | 0,9758 | 0,9210 |
| 6 | 0,8016 | 0 | 0,9645 | 0,9596 | 0,9694 |
| 11 | 0,9142 | 0,9645 | 0 | 0,9017 | 0,9587 |
| 16 | 0,9758 | 0,9596 | 0,9017 | 0 | 0,9440 |
| 19 | 0,9210 | 0,9694 | 0,9587 | 0,9440 | 0 |

**Pasos 1 y 2 (iguales en los tres criterios).** La menor distancia es 0,8016, así que se unen 2 y 6. Después se unen 11 y 16 a 0,9017. Lo que cambia es cómo se actualizan las distancias del grupo {2, 6}:

| Distancia | Single (mín) | Complete (máx) | Average (promedio) |
|---|---|---|---|
| d({2, 6}, 11) | mín(0,9142; 0,9645) = 0,9142 | máx(0,9142; 0,9645) = 0,9645 | (0,9142 + 0,9645)/2 = 0,9393 |
| d({2, 6}, 16) | mín(0,9758; 0,9596) = 0,9596 | máx(0,9758; 0,9596) = 0,9758 | (0,9758 + 0,9596)/2 = 0,9677 |
| d({2, 6}, 19) | mín(0,9210; 0,9694) = 0,9210 | máx(0,9210; 0,9694) = 0,9694 | (0,9210 + 0,9694)/2 = 0,9452 |

**Paso 3 (aquí se separan los criterios).** Quedan tres grupos: 19, {2, 6} y {11, 16}.

| Criterio | d(19, {2, 6}) | d(19, {11, 16}) | d({2, 6}, {11, 16}) | Unión elegida |
|---|---|---|---|---|
| Single | 0,9210 | 0,9440 | 0,9142 | {2, 6} con {11, 16} a 0,9142 |
| Complete | 0,9694 | 0,9587 | 0,9758 | 19 con {11, 16} a 0,9587 |
| Average | 0,9452 | 0,9513 | 0,9535 | 19 con {2, 6} a 0,9452 |

En el paso 4 se une lo que queda: a 0,9210 (single), 0,9758 (complete) y 0,9528 (average). En el average, la última distancia pondera por tamaños: d({2, 6, 19}, {11, 16}) = (1·0,9513 + 2·0,9535)/3 = 0,9528.

La figura `resultados/req2_caso_dendrogramas.png` muestra los tres árboles. La correlación cofenética de este caso, con 10 pares, es 0,8992 (single), 0,9132 (complete) y 0,9255 (average).

## 6.6 Resultados con los 20 abstracts

Los dendrogramas están en `resultados/req2_dendrograma_single.png`, `req2_dendrograma_complete.png` y `req2_dendrograma_average.png`. La primera unión es la misma en los tres (artículos 2 y 6 a 0,8016), porque al principio todos los grupos tienen un solo elemento y los tres criterios coinciden.

| Criterio | Correlación cofenética | Altura de la raíz | Grupos al cortar el árbol en 4 |
|---|---|---|---|
| Single | 0,7630 | 0,9434 | {1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20}, {3}, {4}, {14} |
| Complete | 0,7322 | 0,9990 | {1, 4, 13}, {2, 5, 6, 7, 9, 12, 15, 18, 20}, {3, 8, 10, 14, 17}, {11, 16, 19} |
| Average | **0,8077** | 0,9733 | {1, 13}, {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 20}, {14}, {19} |

## 6.7 Análisis: ¿cuál criterio agrupa mejor?

Según la métrica interna, **Average linkage es el criterio más coherente**, con una correlación cofenética de 0,8077, seguido de Single (0,7630) y Complete (0,7322). Es el resultado esperado: el promedio usa todas las distancias entre los dos grupos, mientras que Single y Complete dependen de un solo par de puntos (el más cercano o el más lejano), de modo que el árbol deforma más las distancias reales.

La tabla de grupos muestra el comportamiento típico de cada criterio:

- **Single** produce un encadenamiento: un grupo va absorbiendo abstracts uno por uno (desde el paso 11 del archivo de uniones, cada unión agrega un solo artículo al grupo grande), porque basta con que un solo punto del grupo esté cerca. Al cortar en 4 quedan un grupo de 17 y tres artículos sueltos.
- **Complete** forma grupos más equilibrados y fáciles de interpretar, como {11, 16, 19}: los tres hablan de IA generativa y ChatGPT en la evaluación y la educación. A cambio, su raíz llega a 0,9990 y es el que más se aleja de las distancias reales.
- **Average** queda en medio: conserva mejor las distancias, pero con estos datos también forma un grupo grande, porque 181 de las 190 distancias están entre 0,90 y 1.

La correlación cofenética mide qué tan fiel es el árbol a las distancias, no si los grupos son equilibrados o temáticos. Por eso el documento reporta el ganador por la métrica (Average) y también señala que Complete da la partición más fácil de leer. La causa de fondo es la matriz: el promedio de las distancias es 0,9568, porque con abstracts cortos y TF-IDF dos textos solo se acercan si comparten palabras poco comunes.

## 6.8 Verificación

`pruebas_clustering.py` ejecuta tres comprobaciones, y todas pasan:

| Prueba | Qué compara | Casos |
|---|---|---|
| Caso a mano | Puntos 0, 1, 3 y 7 en una recta; alturas calculadas a mano para los tres criterios, matriz cofenética, correlación igual a 1 en un árbol perfecto y corte en 2 grupos | 1 |
| Definición de cada criterio | Alturas de `agrupar` contra una versión lenta que recorre todos los pares de puntos | 2.000 matrices de 2 a 12 elementos |
| scipy (solo verificación) | Alturas y correlación cofenética contra `scipy.cluster.hierarchy.linkage` y `cophenet` | 300 matrices de 3 a 20 elementos |