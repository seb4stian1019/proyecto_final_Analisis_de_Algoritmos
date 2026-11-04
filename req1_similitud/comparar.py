"""
REQUERIMIENTO 1 - Similitud entre dos o más abstracts elegidos por el usuario
==============================================================================
El usuario elige dos o más artículos (por su número, 1 a 20) y el programa
compara cada par de abstracts con los seis algoritmos:

  Clásicos (similitud.py)                 Con IA (vectores de embeddings.py)
  1. Levenshtein   (programación dinámica)   5. GloVe  + coseno
  2. LCS           (programación dinámica)   6. MiniLM + coseno
  3. Jaccard       (conjuntos)
  4. Coseno TF-IDF (espacio vectorial)

Sin argumentos, calcula además la matriz 20 x 20 de cada algoritmo y la guarda
en resultados/ (la usan el análisis crítico y el Requerimiento 2).

Uso:  python -m req1_similitud.comparar 11 16          (dos artículos)
      python -m req1_similitud.comparar 3 11 16 18     (cuatro artículos: 6 pares)
      python -m req1_similitud.comparar                (matrices completas)
"""

import csv
import json
import sys

from req1_similitud import similitud as s
from paso1_corpus.datos import RESULTADOS, cargar_corpus

NOMBRES = ["Levenshtein", "LCS", "Jaccard", "Coseno TF-IDF", "GloVe", "MiniLM"]


class Comparador:
    """Prepara todo lo que se necesita una sola vez (palabras, idf y vectores)
    y luego compara cualquier par de artículos con los seis algoritmos."""

    def __init__(self, corpus):
        self.corpus = {a["id"]: a for a in corpus}
        self.palabras = {a["id"]: s.preprocesar(a["abstract"]) for a in corpus}
        self.tfidf = s.ModeloTFIDF(list(self.palabras.values()))
        ruta = RESULTADOS / "req1_embeddings.json"
        if not ruta.exists():
            raise SystemExit("Falta resultados/req1_embeddings.json: ejecute primero  python -m req1_similitud.embeddings")
        modelos = json.loads(ruta.read_text(encoding="utf-8"))
        self.glove = modelos["glove"]["vectores"]
        self.minilm = modelos["minilm"]["vectores"]

    def comparar(self, i, j):
        """Devuelve {algoritmo: similitud} para los artículos i y j."""
        a, b = self.palabras[i], self.palabras[j]
        return {
            "Levenshtein": s.similitud_levenshtein(a, b),
            "LCS": s.similitud_lcs(a, b),
            "Jaccard": s.similitud_jaccard(a, b),
            "Coseno TF-IDF": self.tfidf.similitud(a, b),
            "GloVe": s.coseno_listas(self.glove[str(i)], self.glove[str(j)]),
            "MiniLM": s.coseno_listas(self.minilm[str(i)], self.minilm[str(j)]),
        }


def comparar_seleccion(ids, comparador):
    """Todos los pares posibles entre los artículos elegidos."""
    filas = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            filas.append({"par": (ids[x], ids[y]), **comparador.comparar(ids[x], ids[y])})
    return filas


def matrices(comparador):
    """Matriz 20 x 20 de cada algoritmo (1 en la diagonal). Se guarda en CSV."""
    ids = sorted(comparador.corpus)
    resultado = {n: [[1.0] * len(ids) for _ in ids] for n in NOMBRES}
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            valores = comparador.comparar(ids[x], ids[y])
            for n in NOMBRES:
                resultado[n][x][y] = resultado[n][y][x] = valores[n]
    for n in NOMBRES:
        archivo = RESULTADOS / f"req1_matriz_{n.lower().replace(' ', '_').replace('-', '')}.csv"
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id"] + ids)
            for x, fila in enumerate(resultado[n]):
                w.writerow([ids[x]] + [f"{v:.4f}" for v in fila])
    return ids, resultado


def resumen(ids, resultado):
    """Por algoritmo: promedio, mínimo y máximo fuera de la diagonal, y el par más parecido."""
    filas = []
    for n in NOMBRES:
        pares = [(resultado[n][x][y], ids[x], ids[y])
                 for x in range(len(ids)) for y in range(x + 1, len(ids))]
        valores = [p[0] for p in pares]
        mejor = max(pares)
        filas.append({"algoritmo": n, "promedio": sum(valores) / len(valores),
                      "minimo": min(valores), "maximo": mejor[0], "par_mas_parecido": f"{mejor[1]}-{mejor[2]}"})
    with open(RESULTADOS / "req1_resumen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        for fila in filas:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in fila.items()})
    return filas


def main():
    corpus = cargar_corpus()
    comparador = Comparador(corpus)

    if len(sys.argv) > 1:
        ids = [int(x) for x in sys.argv[1:]]
        if len(ids) < 2 or any(i not in comparador.corpus for i in ids):
            raise SystemExit("Indique dos o más números de artículo entre 1 y 20.")
        for i in ids:
            print(f"[{i:>2}] {comparador.corpus[i]['titulo']}")
        print("\n" + "Par".ljust(8) + "".join(n.rjust(15) for n in NOMBRES))
        for fila in comparar_seleccion(ids, comparador):
            print(f"{fila['par'][0]}-{fila['par'][1]}".ljust(8) + "".join(f"{fila[n]:15.4f}" for n in NOMBRES))
        return

    ids, resultado = matrices(comparador)
    print("Matrices 20 x 20 guardadas en resultados/req1_matriz_*.csv\n")
    print("Algoritmo".ljust(15) + "Promedio".rjust(10) + "Mínimo".rjust(10) + "Máximo".rjust(10) + "   Par más parecido")
    for f in resumen(ids, resultado):
        print(f"{f['algoritmo']:<15}{f['promedio']:10.4f}{f['minimo']:10.4f}{f['maximo']:10.4f}   {f['par_mas_parecido']}")
    print("\nResumen guardado en resultados/req1_resumen.csv")


if __name__ == "__main__":
    main()
