"""
Algoritmos de similitud textual
===============================
Requerimiento 1 del proyecto final (y base del Requerimiento 2).

Todos están programados a mano: solo se usan ciclos, listas, diccionarios,
conjuntos y las funciones math.log y math.sqrt. No se usa ninguna librería que
calcule la similitud por nosotros.

Todas las funciones de similitud devuelven un número entre 0 y 1:
  1 -> los dos textos son iguales (o apuntan en la misma dirección)
  0 -> no tienen nada en común

Los textos se comparan como LISTAS DE PALABRAS (tokens), no letra por letra:
  - es lo que le interesa a la bibliometría (qué temas comparten los abstracts);
  - la matriz de programación dinámica queda de unas 120 x 120 casillas en vez
    de 1.300 x 1.300, y se puede mostrar paso a paso en el documento.
Levenshtein y LCS aceptan igual dos cadenas: en las pruebas se usan con letras.
"""

import math
import re

# ===========================================================================
# 0. Preprocesamiento: texto -> lista de palabras
# ===========================================================================
# Palabras vacías del inglés (artículos, preposiciones, pronombres...). Aparecen en
# todos los abstracts y no dicen nada del tema, así que se eliminan.
PALABRAS_VACIAS = set("""
a about above after again against all also am an and any are as at be because been
before being below between both but by can could did do does doing down during each
few for from further had has have having he her here hers him his how i if in into is
it its itself just may might more most must my no nor not of off on once only or other
our ours out over own same she should so some such than that the their theirs them then
there these they this those through to too under until up us very was we were what
when where which while who whom why will with would you your
""".split())


def preprocesar(texto):
    """'The AI-driven tools, in 2023...' -> ['ai', 'driven', 'tools']
    1. Pasa a minúsculas.
    2. Separa en palabras: secuencias de letras (los números y signos se descartan).
    3. Elimina las palabras vacías y las de una sola letra."""
    palabras = re.findall(r"[a-z]+", texto.lower())
    return [p for p in palabras if len(p) > 1 and p not in PALABRAS_VACIAS]


# ===========================================================================
# 1. Distancia de Levenshtein (programación dinámica)
# ===========================================================================
def matriz_levenshtein(a, b):
    """D[i][j] = mínimo número de operaciones (insertar, borrar o sustituir un
    elemento) para convertir los primeros i elementos de a en los primeros j de b.

    Recurrencia:
        D[i][0] = i                (borrar i elementos)
        D[0][j] = j                (insertar j elementos)
        D[i][j] = D[i-1][j-1]                       si a[i-1] == b[j-1]
                = 1 + min(D[i-1][j],                (borrar a[i-1])
                          D[i][j-1],                (insertar b[j-1])
                          D[i-1][j-1])              (sustituir)
    Costo: O(n·m) en tiempo y en memoria."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                D[i][j] = 1 + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])
    return D


def levenshtein(a, b):
    """Distancia de edición: la casilla final de la matriz."""
    return matriz_levenshtein(a, b)[len(a)][len(b)]


def similitud_levenshtein(a, b):
    """Convierte la distancia en similitud: 1 - distancia / (largo del más largo).
    La distancia nunca supera el largo del más largo, así que queda entre 0 y 1."""
    mayor = max(len(a), len(b))
    if mayor == 0:
        return 1.0
    return 1 - levenshtein(a, b) / mayor


# ===========================================================================
# 2. Subsecuencia común más larga, LCS (programación dinámica)
# ===========================================================================
def matriz_lcs(a, b):
    """L[i][j] = largo de la subsecuencia común más larga entre los primeros i
    elementos de a y los primeros j de b. Una subsecuencia conserva el orden pero
    no tiene que ser continua.

    Recurrencia:
        L[i][0] = L[0][j] = 0
        L[i][j] = L[i-1][j-1] + 1               si a[i-1] == b[j-1]
                = max(L[i-1][j], L[i][j-1])     si no
    Costo: O(n·m) en tiempo y en memoria."""
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L


def reconstruir_lcs(a, b, L):
    """Recorre la matriz desde la esquina final hacia atrás para recuperar
    cuáles elementos forman la subsecuencia. Costo: O(n + m)."""
    i, j, comun = len(a), len(b), []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            comun.append(a[i - 1])
            i, j = i - 1, j - 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    comun.reverse()
    return comun


def similitud_lcs(a, b):
    """Largo de la LCS / largo del más largo (entre 0 y 1)."""
    mayor = max(len(a), len(b))
    if mayor == 0:
        return 1.0
    return matriz_lcs(a, b)[len(a)][len(b)] / mayor


# ===========================================================================
# 3. Coeficiente de Jaccard (conjuntos)
# ===========================================================================
def similitud_jaccard(a, b):
    """|A ∩ B| / |A ∪ B|, donde A y B son los conjuntos de palabras distintas.
    No importa el orden ni cuántas veces se repite cada palabra.
    Costo: O(n + m) en promedio (los conjuntos de Python son tablas hash)."""
    A, B = set(a), set(b)
    union = A | B
    if not union:
        return 1.0
    return len(A & B) / len(union)


# ===========================================================================
# 4. Similitud del coseno con TF-IDF (modelo de espacio vectorial)
# ===========================================================================
def frecuencias(palabras):
    """Cuántas veces aparece cada palabra: ['ai', 'tools', 'ai'] -> {'ai': 2, 'tools': 1}."""
    conteo = {}
    for p in palabras:
        conteo[p] = conteo.get(p, 0) + 1
    return conteo


def calcular_idf(documentos):
    """idf(t) = ln(N / df(t))
    N     = número de documentos (los 20 abstracts)
    df(t) = en cuántos documentos aparece la palabra t
    Una palabra que está en todos los abstracts tiene idf = ln(1) = 0: no sirve
    para distinguirlos. Una palabra rara tiene idf alto."""
    N = len(documentos)
    df = {}
    for palabras in documentos:
        for t in set(palabras):
            df[t] = df.get(t, 0) + 1
    return {t: math.log(N / df[t]) for t in df}


def vector_tfidf(palabras, idf):
    """peso(t) = tf(t) · idf(t), con tf(t) = veces que aparece t / total de palabras.
    El vector se guarda como diccionario {palabra: peso}: solo las palabras que
    aparecen en el abstract (las demás tendrían peso 0)."""
    total = len(palabras)
    return {t: (c / total) * idf.get(t, 0.0) for t, c in frecuencias(palabras).items()}


def coseno_diccionarios(u, v):
    """cos(θ) = (u · v) / (|u| · |v|) para vectores guardados como diccionarios.
    El producto punto solo suma las palabras que están en los dos vectores."""
    producto = 0.0
    for t, peso in u.items():
        if t in v:
            producto += peso * v[t]
    norma_u = math.sqrt(sum(p * p for p in u.values()))
    norma_v = math.sqrt(sum(p * p for p in v.values()))
    if norma_u == 0 or norma_v == 0:
        return 0.0
    return producto / (norma_u * norma_v)


def coseno_listas(u, v):
    """El mismo coseno para vectores densos (listas de números), como los embeddings."""
    producto = 0.0
    norma_u = 0.0
    norma_v = 0.0
    for i in range(len(u)):
        producto += u[i] * v[i]
        norma_u += u[i] * u[i]
        norma_v += v[i] * v[i]
    if norma_u == 0 or norma_v == 0:
        return 0.0
    return producto / (math.sqrt(norma_u) * math.sqrt(norma_v))


class ModeloTFIDF:
    """Calcula el idf con TODO el corpus (los 20 abstracts) una sola vez, y luego
    compara cualquier par de abstracts. Usar el corpus completo hace que el peso
    de cada palabra no cambie según cuáles artículos elija el usuario."""

    def __init__(self, documentos):
        self.idf = calcular_idf(documentos)

    def vector(self, palabras):
        return vector_tfidf(palabras, self.idf)

    def similitud(self, a, b):
        return coseno_diccionarios(self.vector(a), self.vector(b))


# ===========================================================================
# 5. Matriz de similitud (la usa el Requerimiento 2)
# ===========================================================================
def matriz_similitud(documentos, funcion):
    """S[i][j] = funcion(documentos[i], documentos[j]) para todos los pares.
    Es simétrica, así que se calcula solo la mitad. Costo: O(N²) llamadas."""
    N = len(documentos)
    S = [[1.0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            S[i][j] = S[j][i] = funcion(documentos[i], documentos[j])
    return S
