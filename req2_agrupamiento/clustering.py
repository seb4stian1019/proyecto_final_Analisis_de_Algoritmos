"""
Agrupamiento jerárquico aglomerativo
====================================
Requerimiento 2 del proyecto final.

Todo está programado a mano: solo se usan ciclos, listas, diccionarios y
math.sqrt. No se usa scipy, sklearn ni ninguna librería que agrupe por nosotros
(scipy aparece solo en pruebas.py, para comprobar los resultados).
matplotlib solo dibuja las líneas del dendrograma que calculamos aquí.

Idea del algoritmo (igual para los tres criterios):
  1. Cada abstract empieza siendo un grupo propio  -> 20 grupos.
  2. Se buscan los dos grupos más cercanos y se unen en uno nuevo.
  3. Se calcula la distancia del grupo nuevo a todos los demás.
     Aquí es donde cambia el criterio:
        Single   (enlace simple):    distancia entre los dos puntos MÁS cercanos
        Complete (enlace completo):  distancia entre los dos puntos MÁS lejanos
        Average  (enlace promedio):  promedio de todas las distancias entre puntos
  4. Se repite hasta que queda un solo grupo (19 uniones para 20 abstracts).

Cada unión se guarda como (grupo_a, grupo_b, altura, tamaño). Los grupos se
numeran como en la literatura: 0..n-1 son los abstracts (hojas) y la unión
número k crea el grupo n + k. Esta lista de uniones ES el árbol (dendrograma).
"""

import math

from req1_similitud.similitud import ModeloTFIDF, coseno_diccionarios, preprocesar

CRITERIOS = ("single", "complete", "average")


# ===========================================================================
# 1. Preprocesamiento + similitud -> matriz de distancias
# ===========================================================================
def matriz_distancias(abstracts):
    """D[i][j] = 1 - coseno(TF-IDF de i, TF-IDF de j).
    Se reutilizan las funciones del Requerimiento 1 (req1_similitud/similitud.py):
      - preprocesar: minúsculas, solo letras, sin palabras vacías;
      - ModeloTFIDF: idf calculado con los 20 abstracts y coseno a mano.
    El coseno está entre 0 y 1, así que la distancia también:
      0 -> abstracts con el mismo vocabulario,  1 -> sin ninguna palabra en común."""
    documentos = [preprocesar(a) for a in abstracts]
    modelo = ModeloTFIDF(documentos)
    vectores = [modelo.vector(d) for d in documentos]

    n = len(documentos)
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            D[i][j] = D[j][i] = 1.0 - coseno_diccionarios(vectores[i], vectores[j])
    return D


# ===========================================================================
# 2. Distancia del grupo nuevo a otro grupo (lo único que cambia por criterio)
# ===========================================================================
def distancia_nueva(criterio, d_ax, d_bx, tam_a, tam_b):
    """Distancia del grupo (a ∪ b) a otro grupo x, a partir de d(a, x) y d(b, x).

    single:   min(d(a,x), d(b,x))
    complete: max(d(a,x), d(b,x))
    average:  (|a|·d(a,x) + |b|·d(b,x)) / (|a| + |b|)

    Las tres fórmulas dan exactamente lo mismo que recorrer todos los pares de
    puntos (el mínimo, el máximo o el promedio), pero en O(1): no hace falta
    volver a mirar los abstracts uno por uno."""
    if criterio == "single":
        return d_ax if d_ax < d_bx else d_bx
    if criterio == "complete":
        return d_ax if d_ax > d_bx else d_bx
    if criterio == "average":
        return (tam_a * d_ax + tam_b * d_bx) / (tam_a + tam_b)
    raise ValueError(f"Criterio desconocido: {criterio}")


# ===========================================================================
# 3. Algoritmo aglomerativo
# ===========================================================================
def agrupar(D, criterio, traza=False):
    """Devuelve la lista de uniones [(a, b, altura, tamaño), ...] (n - 1 uniones).
    Con traza=True devuelve además, para cada paso, la matriz de distancias entre
    los grupos activos ANTES de unir (sirve para el caso de estudio).

    Costo: hay n - 1 uniones; en cada una se busca el par más cercano entre
    k grupos activos (O(k²)) y se actualizan k distancias (O(k)).
    Total: Σ k(k-1)/2 = O(n³) en tiempo y O(n²) en memoria. Con n = 20 se
    revisan 1.330 pares en total (C(21, 3)), nada para el computador."""
    n = len(D)
    # dist[g][h]: distancia entre los grupos activos g y h (diccionario de diccionarios,
    # así se pueden borrar los grupos que se unen y agregar el nuevo).
    dist = {i: {j: D[i][j] for j in range(n) if j != i} for i in range(n)}
    tam = {i: 1 for i in range(n)}
    uniones = []
    pasos = []

    for k in range(n - 1):
        activos = sorted(dist)
        if traza:
            pasos.append({
                "grupos": activos,
                "matriz": [[0.0 if g == h else dist[g][h] for h in activos] for g in activos],
            })

        # 1) Par más cercano. En empate gana el par con números menores, para que el
        #    resultado sea siempre el mismo.
        mejor = None
        for x in range(len(activos)):
            for y in range(x + 1, len(activos)):
                g, h = activos[x], activos[y]
                if mejor is None or dist[g][h] < mejor[2]:
                    mejor = (g, h, dist[g][h])
        a, b, altura = mejor

        # 2) Se crea el grupo nuevo n + k y se calcula su distancia a los demás.
        nuevo = n + k
        dist[nuevo] = {}
        for x in activos:
            if x == a or x == b:
                continue
            d = distancia_nueva(criterio, dist[a][x], dist[b][x], tam[a], tam[b])
            dist[nuevo][x] = d
            dist[x][nuevo] = d

        # 3) Se borran a y b de la matriz.
        for g in (a, b):
            for x in dist[g]:
                if x != a and x != b:
                    del dist[x][g]
            del dist[g]

        tam[nuevo] = tam[a] + tam[b]
        uniones.append((a, b, altura, tam[nuevo]))
        if traza:
            pasos[-1]["union"] = (a, b, altura, nuevo)

    return (uniones, pasos) if traza else uniones


def miembros(uniones, n):
    """miembros[g] = lista de abstracts (hojas) que hay dentro del grupo g."""
    m = {i: [i] for i in range(n)}
    for k, (a, b, _, _) in enumerate(uniones):
        m[n + k] = m[a] + m[b]
    return m


# ===========================================================================
# 4. Métrica interna: coeficiente de correlación cofenética
# ===========================================================================
def matriz_cofenetica(uniones, n):
    """C[i][j] = altura del dendrograma a la que i y j quedan por primera vez en
    el mismo grupo. Es la distancia que "cree" el árbol entre los dos abstracts."""
    C = [[0.0] * n for _ in range(n)]
    m = miembros(uniones, n)
    for a, b, altura, _ in uniones:
        for i in m[a]:
            for j in m[b]:
                C[i][j] = C[j][i] = altura
    return C


def correlacion_cofenetica(D, C):
    """Correlación de Pearson entre las distancias originales D[i][j] y las
    cofenéticas C[i][j], usando los n(n-1)/2 pares i < j:

        r = Σ (d - d̄)(c - c̄) / sqrt( Σ (d - d̄)² · Σ (c - c̄)² )

    r cerca de 1: el dendrograma respeta bien las distancias reales.
    Gana el criterio con el r más alto. Costo: O(n²)."""
    n = len(D)
    d = [D[i][j] for i in range(n) for j in range(i + 1, n)]
    c = [C[i][j] for i in range(n) for j in range(i + 1, n)]
    p = len(d)
    media_d = sum(d) / p
    media_c = sum(c) / p
    num = 0.0
    sd = 0.0
    sc = 0.0
    for t in range(p):
        num += (d[t] - media_d) * (c[t] - media_c)
        sd += (d[t] - media_d) ** 2
        sc += (c[t] - media_c) ** 2
    if sd == 0 or sc == 0:
        return 0.0
    return num / math.sqrt(sd * sc)


# ===========================================================================
# 5. Cortar el árbol en k grupos (para describir qué temas se forman)
# ===========================================================================
def cortar(uniones, n, k):
    """Deshace las k - 1 últimas uniones y devuelve los k grupos resultantes
    (listas de índices de abstracts)."""
    m = miembros(uniones, n)
    grupos = [n + len(uniones) - 1]          # se empieza con la raíz
    while len(grupos) < k:
        # El grupo con número más alto es la unión más reciente (la más alta del
        # árbol): se separa en sus dos hijos.
        ultimo = max(grupos)
        grupos.remove(ultimo)
        a, b, _, _ = uniones[ultimo - n]
        grupos += [a, b]
    return sorted((sorted(m[g]) for g in grupos), key=lambda x: x[0])


# ===========================================================================
# 6. Dendrograma
# ===========================================================================
def orden_hojas(uniones, n):
    """Orden de las hojas de izquierda a derecha: recorrido en profundidad del
    árbol empezando por la raíz (así las ramas nunca se cruzan)."""
    orden = []
    pila = [n + len(uniones) - 1]
    while pila:
        g = pila.pop()
        if g < n:
            orden.append(g)
        else:
            a, b, _, _ = uniones[g - n]
            pila.append(b)          # se apila b primero para visitar a primero
            pila.append(a)
    return orden


def coordenadas_dendrograma(uniones, n):
    """Para cada unión devuelve las líneas en forma de U invertida:
    ([x_a, x_a, x_b, x_b], [y_a, altura, altura, y_b]).
    x de una hoja = su posición en orden_hojas; x de un grupo = punto medio de sus
    dos hijos; y de una hoja = 0; y de un grupo = altura de su unión."""
    pos = {g: float(i) for i, g in enumerate(orden_hojas(uniones, n))}
    alt = {i: 0.0 for i in range(n)}
    lineas = []
    for k, (a, b, altura, _) in enumerate(uniones):
        lineas.append(([pos[a], pos[a], pos[b], pos[b]], [alt[a], altura, altura, alt[b]]))
        pos[n + k] = (pos[a] + pos[b]) / 2
        alt[n + k] = altura
    return lineas


def dibujar_dendrograma(uniones, etiquetas, titulo, ruta):
    """Dibuja el dendrograma con las coordenadas calculadas arriba.
    matplotlib solo traza las líneas; no calcula nada del agrupamiento."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(etiquetas)
    fig, ax = plt.subplots(figsize=(10, 5))
    for xs, ys in coordenadas_dendrograma(uniones, n):
        ax.plot(xs, ys, color="#1f4e79", linewidth=1.4)
    orden = orden_hojas(uniones, n)
    ax.set_xticks(range(n))
    ax.set_xticklabels([etiquetas[i] for i in orden])
    ax.set_xlabel("Artículo")
    ax.set_ylabel("Distancia (1 − coseno TF-IDF)")
    ax.set_title(titulo)
    ax.set_xlim(-0.6, n - 0.4)
    # Todas las uniones ocurren por encima de la primera altura, así que el eje Y
    # empieza un poco antes de ella para que se vea la estructura del árbol.
    minima = min(u[2] for u in uniones)
    maxima = max(u[2] for u in uniones)
    ax.set_ylim(max(0.0, minima - 0.1), maxima + 0.02)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)