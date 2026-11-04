"""
Pruebas de los algoritmos de similitud (Requerimiento 1)
========================================================
1. Casos pequeños resueltos a mano (se pueden verificar en papel).
2. 3.000 pares de cadenas aleatorias: Levenshtein y LCS se comparan con una
   versión recursiva directa de su definición (lenta, pero obviamente correcta).
3. Propiedades que toda similitud debe cumplir: valor entre 0 y 1, simetría
   sim(a, b) = sim(b, a) y sim(a, a) = 1.

Uso: python -m req1_similitud.pruebas
"""

import math
import random
from functools import lru_cache

from req1_similitud import similitud as s

# (descripción, valor obtenido, valor esperado) -> resueltos a mano
CASOS = [
    ("levenshtein('kitten', 'sitting')", s.levenshtein("kitten", "sitting"), 3),
    ("levenshtein('', 'abc')", s.levenshtein("", "abc"), 3),
    ("levenshtein('abc', 'abc')", s.levenshtein("abc", "abc"), 0),
    ("levenshtein de palabras", s.levenshtein(["ai", "tools", "help"], ["ai", "help"]), 1),
    ("similitud_levenshtein('kitten', 'sitting')", s.similitud_levenshtein("kitten", "sitting"), 1 - 3 / 7),
    ("LCS('ABCBDAB', 'BDCABA')", s.matriz_lcs("ABCBDAB", "BDCABA")[7][6], 4),
    ("reconstruir LCS('AGGTAB', 'GXTXAYB')",
     "".join(s.reconstruir_lcs("AGGTAB", "GXTXAYB", s.matriz_lcs("AGGTAB", "GXTXAYB"))), "GTAB"),
    ("jaccard({a,b,c}, {b,c,d})", s.similitud_jaccard(["a", "b", "c"], ["b", "c", "d"]), 2 / 4),
    ("jaccard con repetidos", s.similitud_jaccard(["a", "a", "b"], ["a"]), 1 / 2),
    ("coseno de [1,0] y [0,1]", s.coseno_listas([1, 0], [0, 1]), 0.0),
    ("coseno de [1,2,3] y [2,4,6]", s.coseno_listas([1, 2, 3], [2, 4, 6]), 1.0),
    ("coseno de [3,4] y [4,3]", s.coseno_listas([3, 4], [4, 3]), 24 / 25),
    ("coseno de diccionarios", s.coseno_diccionarios({"a": 3, "b": 4}, {"b": 3, "a": 4}), 24 / 25),
    ("preprocesar", s.preprocesar("The AI-driven tools, in 2023, are a help."), ["ai", "driven", "tools", "help"]),
]

# TF-IDF a mano con 3 documentos:
#   d1 = [ai, ai, data]   d2 = [ai, learning]   d3 = [data, learning, learning]
#   df: ai=2, data=2, learning=2 -> idf = ln(3/2) para las tres palabras
#   tf en d1: ai=2/3, data=1/3  -> vector d1 = (2/3·idf, 1/3·idf, 0)
DOCS = [["ai", "ai", "data"], ["ai", "learning"], ["data", "learning", "learning"]]
IDF = math.log(3 / 2)
TFIDF = s.ModeloTFIDF(DOCS)
CASOS += [
    ("idf de 'ai'", TFIDF.idf["ai"], IDF),
    ("tf-idf de 'ai' en d1", TFIDF.vector(DOCS[0])["ai"], 2 / 3 * IDF),
    # d1 = idf·(2/3, 1/3, 0), d2 = idf·(1/2, 0, 1/2): cos = (1/3) / (sqrt(5/9)·sqrt(1/2))
    ("coseno tf-idf d1-d2", TFIDF.similitud(DOCS[0], DOCS[1]), (1 / 3) / (math.sqrt(5 / 9) * math.sqrt(1 / 2))),
]


def levenshtein_recursivo(a, b):
    """La definición tal cual, con recursión (exponencial sin memoria)."""
    @lru_cache(maxsize=None)
    def d(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return d(i - 1, j - 1)
        return 1 + min(d(i - 1, j), d(i, j - 1), d(i - 1, j - 1))
    return d(len(a), len(b))


def lcs_recursivo(a, b):
    @lru_cache(maxsize=None)
    def l(i, j):
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return l(i - 1, j - 1) + 1
        return max(l(i - 1, j), l(i, j - 1))
    return l(len(a), len(b))


def es_subsecuencia(sub, texto):
    """True si sub aparece dentro de texto en el mismo orden (no necesariamente seguido)."""
    i = 0
    for c in texto:
        if i < len(sub) and sub[i] == c:
            i += 1
    return i == len(sub)


def main():
    fallos = 0
    for nombre, obtenido, esperado in CASOS:
        iguales = (abs(obtenido - esperado) < 1e-12 if isinstance(esperado, float) else obtenido == esperado)
        if not iguales:
            fallos += 1
            print(f"FALLO {nombre}: {obtenido} != {esperado}")
    print(f"Casos a mano: {len(CASOS)}")

    random.seed(2026)
    aleatorios = 3_000
    funciones = [s.similitud_levenshtein, s.similitud_lcs, s.similitud_jaccard]
    for _ in range(aleatorios):
        alfabeto = random.choice(["ab", "abc", "abcdefgh"])
        a = "".join(random.choice(alfabeto) for _ in range(random.randint(0, 12)))
        b = "".join(random.choice(alfabeto) for _ in range(random.randint(0, 12)))
        if s.levenshtein(a, b) != levenshtein_recursivo(a, b):
            fallos += 1
            print(f"FALLO Levenshtein: '{a}' '{b}'")
        L = s.matriz_lcs(a, b)
        comun = s.reconstruir_lcs(a, b, L)
        if L[len(a)][len(b)] != lcs_recursivo(a, b) or len(comun) != L[len(a)][len(b)] \
                or not es_subsecuencia(comun, a) or not es_subsecuencia(comun, b):
            fallos += 1
            print(f"FALLO LCS: '{a}' '{b}'")
        for f in funciones:
            ab, ba = f(a, b), f(b, a)
            if not (0 <= ab <= 1) or abs(ab - ba) > 1e-12 or abs(f(a, a) - 1) > 1e-12:
                fallos += 1
                print(f"FALLO propiedades de {f.__name__}: '{a}' '{b}'")
    print(f"Pares aleatorios: {aleatorios:,}".replace(",", ".") +
          " (Levenshtein y LCS contra la definición recursiva; rango, simetría y sim(a, a) = 1)")
    print("\nResultado:", "TODAS LAS PRUEBAS PASARON" if fallos == 0 else f"{fallos} FALLOS")


if __name__ == "__main__":
    main()
