"""
Pruebas del agrupamiento jerárquico (clustering.py)
===================================================
1. Un caso calculado a mano: 4 puntos en una recta (0, 1, 3 y 7).
2. 2.000 matrices aleatorias contra la DEFINICIÓN de cada criterio: un
   agrupamiento "lento" que en cada paso recorre todos los pares de puntos
   (mínimo, máximo o promedio) en vez de usar la fórmula de actualización.
3. Si scipy está instalado, 300 matrices aleatorias contra
   scipy.cluster.hierarchy.linkage y cophenet. scipy se usa SOLO aquí, para
   verificar; el proyecto no lo necesita (no está en requirements.txt).

Uso:  python -m req2_agrupamiento.pruebas
"""

import math
import random

from req2_agrupamiento import clustering as cl


def cerca(x, y, tol=1e-9):
    return abs(x - y) <= tol


def caso_a_mano():
    """Puntos 0, 1, 3, 7 -> D[i][j] = |x_i - x_j|.
    Single:   {0,1} a 1;  {0,1,3} a min(3, 2) = 2;          todo a min(7, 6, 4) = 4
    Complete: {0,1} a 1;  {0,1,3} a max(3, 2) = 3;          todo a max(7, 6, 4) = 7
    Average:  {0,1} a 1;  {0,1,3} a (3 + 2)/2 = 2,5;        todo a (7 + 6 + 4)/3 = 5,667"""
    x = [0, 1, 3, 7]
    D = [[abs(a - b) for b in x] for a in x]
    esperado = {
        "single": [(0, 1, 1), (2, 4, 2), (3, 5, 4)],
        "complete": [(0, 1, 1), (2, 4, 3), (3, 5, 7)],
        "average": [(0, 1, 1), (2, 4, 2.5), (3, 5, 17 / 3)],
    }
    for criterio, uniones_esp in esperado.items():
        uniones = cl.agrupar(D, criterio)
        for (a, b, h, _), (ea, eb, eh) in zip(uniones, uniones_esp):
            assert {a, b} == {ea, eb} and cerca(h, eh), (criterio, uniones)
    # Cofenética del single: 0-1 a 1; 0-3 y 1-3 a 2; todos con 7 a 4.
    C = cl.matriz_cofenetica(cl.agrupar(D, "single"), 4)
    assert C[0][1] == 1 and C[0][2] == 2 and C[1][2] == 2 and C[0][3] == C[2][3] == 4
    # Si el árbol reproduce exactamente las distancias, la correlación es 1.
    D_ultra = [[0, 1, 2, 2], [1, 0, 2, 2], [2, 2, 0, 1], [2, 2, 1, 0]]
    assert cerca(cl.correlacion_cofenetica(D_ultra, D_ultra), 1.0)
    # cortar: con k = 2 en el single quedan {0, 1, 3} y {7}.
    assert cl.cortar(cl.agrupar(D, "single"), 4, 2) == [[0, 1, 2], [3]]
    print("Caso a mano (puntos 0, 1, 3, 7): correcto")


def agrupar_por_definicion(D, criterio):
    """Versión lenta y obvia: en cada paso calcula la distancia entre cada par de
    grupos recorriendo TODOS los pares de puntos. Devuelve las alturas."""
    grupos = [[i] for i in range(len(D))]
    alturas = []
    while len(grupos) > 1:
        mejor = None
        for x in range(len(grupos)):
            for y in range(x + 1, len(grupos)):
                ds = [D[i][j] for i in grupos[x] for j in grupos[y]]
                if criterio == "single":
                    d = min(ds)
                elif criterio == "complete":
                    d = max(ds)
                else:
                    d = sum(ds) / len(ds)
                if mejor is None or d < mejor[0]:
                    mejor = (d, x, y)
        d, x, y = mejor
        alturas.append(d)
        grupos[x] = grupos[x] + grupos[y]
        del grupos[y]
    return alturas


def matriz_aleatoria(n, rng):
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            D[i][j] = D[j][i] = rng.random()   # sin empates en la práctica
    return D


def contra_definicion(casos=2000):
    rng = random.Random(2026)
    for _ in range(casos):
        n = rng.randint(2, 12)
        D = matriz_aleatoria(n, rng)
        for criterio in cl.CRITERIOS:
            rapidas = [u[2] for u in cl.agrupar(D, criterio)]
            lentas = agrupar_por_definicion(D, criterio)
            assert all(cerca(a, b) for a, b in zip(rapidas, lentas)), (criterio, D)
    print(f"{casos} matrices aleatorias contra la definición de cada criterio: correcto")


def contra_scipy(casos=300):
    try:
        import numpy as np
        from scipy.cluster.hierarchy import cophenet, linkage
        from scipy.spatial.distance import squareform
    except ImportError:
        print("scipy no está instalado: se omite la comparación con scipy")
        return
    rng = random.Random(7)
    for _ in range(casos):
        n = rng.randint(3, 20)
        D = matriz_aleatoria(n, rng)
        condensada = squareform(np.array(D), checks=False)
        for criterio in cl.CRITERIOS:
            uniones = cl.agrupar(D, criterio)
            Z = linkage(condensada, method=criterio)
            assert all(cerca(u[2], z) for u, z in zip(uniones, Z[:, 2])), criterio
            r = cl.correlacion_cofenetica(D, cl.matriz_cofenetica(uniones, n))
            assert cerca(r, cophenet(Z, condensada)[0], 1e-9), criterio
    print(f"{casos} matrices aleatorias contra scipy (alturas y correlación cofenética): correcto")


def main():
    caso_a_mano()
    contra_definicion()
    contra_scipy()


if __name__ == "__main__":
    main()