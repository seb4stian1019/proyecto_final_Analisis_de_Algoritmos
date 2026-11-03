"""
REQUERIMIENTO 2 - Agrupamiento jerárquico de los 20 abstracts
=============================================================
1. Preprocesamiento: cada abstract -> lista de palabras (similitud.preprocesar).
2. Similitud: coseno con TF-IDF; distancia = 1 - coseno (matriz 20 x 20).
3. Clustering: Single, Complete y Average linkage, programados en clustering.py.
4. Dendrograma: uno por criterio (PNG).
5. Evaluación: coeficiente de correlación cofenética de cada criterio.

Archivos que genera en resultados/:
  req2_distancias.csv              matriz de distancias 20 x 20
  req2_uniones_<criterio>.csv      las 19 uniones (el árbol) de cada criterio
  req2_dendrograma_<criterio>.png  dendrograma de cada criterio
  req2_evaluacion.csv              correlación cofenética y grupos al cortar en k = 4

Uso:  python -m req2_agrupamiento.dendrogramas
"""

import csv

from req2_agrupamiento import clustering as cl
from paso1_corpus.datos import	 RESULTADOS, cargar_corpus

NOMBRES = {"single": "Single linkage (enlace simple)",
           "complete": "Complete linkage (enlace completo)",
           "average": "Average linkage (enlace promedio)"}
K_CORTE = 4


def main():
    corpus = cargar_corpus()
    ids = [a["id"] for a in corpus]
    n = len(ids)
    RESULTADOS.mkdir(exist_ok=True)

    D = cl.matriz_distancias([a["abstract"] for a in corpus])
    with open(RESULTADOS / "req2_distancias.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["articulo"] + ids)
        for i in range(n):
            w.writerow([ids[i]] + [f"{D[i][j]:.6f}" for j in range(n)])

    filas = []
    for criterio in cl.CRITERIOS:
        uniones = cl.agrupar(D, criterio)
        C = cl.matriz_cofenetica(uniones, n)
        r = cl.correlacion_cofenetica(D, C)
        m = cl.miembros(uniones, n)

        with open(RESULTADOS / f"req2_uniones_{criterio}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["paso", "grupo_a", "grupo_b", "grupo_nuevo", "altura", "tamano", "articulos"])
            for k, (a, b, altura, tam) in enumerate(uniones):
                arts = " ".join(str(ids[i]) for i in sorted(m[n + k]))
                w.writerow([k + 1, a, b, n + k, f"{altura:.6f}", tam, arts])

        cl.dibujar_dendrograma(uniones, [str(x) for x in ids],
                               f"{NOMBRES[criterio]} · correlación cofenética = {r:.4f}",
                               RESULTADOS / f"req2_dendrograma_{criterio}.png")

        grupos = cl.cortar(uniones, n, K_CORTE)
        texto_grupos = " | ".join(" ".join(str(ids[i]) for i in g) for g in grupos)
        filas.append((criterio, r, uniones[-1][2], texto_grupos))

        print(f"\n{NOMBRES[criterio]}")
        print(f"  Correlación cofenética: {r:.4f}")
        print(f"  Primera unión: artículos {ids[uniones[0][0]]} y {ids[uniones[0][1]]} "
              f"(distancia {uniones[0][2]:.4f})")
        print(f"  Grupos al cortar en {K_CORTE}: {texto_grupos}")

    with open(RESULTADOS / "req2_evaluacion.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["criterio", "correlacion_cofenetica", "altura_raiz", f"grupos_k{K_CORTE}"])
        for criterio, r, raiz, grupos in filas:
            w.writerow([criterio, f"{r:.6f}", f"{raiz:.6f}", grupos])

    mejor = max(filas, key=lambda x: x[1])
    print(f"\nCriterio con la correlación cofenética más alta: {NOMBRES[mejor[0]]} ({mejor[1]:.4f})")
    print("Archivos guardados en resultados/ (req2_*.csv y req2_dendrograma_*.png)")


if __name__ == "__main__":
    main()