"""
REQUERIMIENTO 2 - Caso de estudio paso a paso
=============================================
Se toman 5 artículos (2, 6, 11, 16 y 19) y se muestra, para cada criterio:
  - la matriz de distancias entre los grupos activos en cada paso;
  - qué par se une y a qué altura;
  - cómo se calcula la distancia del grupo nuevo a los demás (mín, máx o promedio);
  - la matriz cofenética y la correlación cofenética.

Las distancias salen de la matriz 20 x 20 (el idf se calcula con los 20 abstracts),
así que coinciden con resultados/req2_distancias.csv.

Se eligieron estos 5 porque el 2 y el 6 son el par más cercano de todo el corpus,
el 11 y el 16 son los del caso de estudio del Requerimiento 1, y con el 19 los
tres criterios toman decisiones distintas desde el tercer paso.

Genera resultados/req2_caso_estudio.json y resultados/req2_caso_dendrogramas.png
Uso:  python -m req2_agrupamiento.caso_estudio
"""

import json

from req2_agrupamiento import clustering as cl
from paso1_corpus.datos import	 RESULTADOS, cargar_corpus

CASO = [2, 6, 11, 16, 19]


def nombre_grupo(g, m, etiquetas):
    """'{2, 6}' para un grupo, '2' para una hoja."""
    arts = sorted(etiquetas[i] for i in m[g])
    return str(arts[0]) if len(arts) == 1 else "{" + ", ".join(map(str, arts)) + "}"


def imprimir_matriz(titulo, nombres, M):
    ancho = max(8, max(len(x) for x in nombres) + 1)
    print(titulo)
    print(" " * ancho + "".join(f"{x:>{ancho}}" for x in nombres))
    for x, fila in zip(nombres, M):
        print(f"{x:>{ancho}}" + "".join(f"{v:>{ancho}.4f}" for v in fila))


def main():
    corpus = cargar_corpus()
    pos = {a["id"]: k for k, a in enumerate(corpus)}
    D20 = cl.matriz_distancias([a["abstract"] for a in corpus])
    idx = [pos[i] for i in CASO]
    D = [[D20[i][j] for j in idx] for i in idx]
    n = len(CASO)

    salida = {"articulos": CASO,
              "titulos": {i: corpus[pos[i]]["titulo"] for i in CASO},
              "distancias": D,
              "criterios": {}}

    imprimir_matriz("Matriz de distancias inicial (1 - coseno TF-IDF)", [str(x) for x in CASO], D)

    for criterio in cl.CRITERIOS:
        uniones, pasos = cl.agrupar(D, criterio, traza=True)
        m = cl.miembros(uniones, n)
        tam = {g: len(m[g]) for g in m}
        print(f"\n================ {criterio.upper()} ================")
        pasos_json = []
        for k, paso in enumerate(pasos):
            nombres = [nombre_grupo(g, m, CASO) for g in paso["grupos"]]
            a, b, altura, nuevo = paso["union"]
            imprimir_matriz(f"\nPaso {k + 1}: grupos activos", nombres, paso["matriz"])
            print(f"-> Se unen {nombre_grupo(a, m, CASO)} y {nombre_grupo(b, m, CASO)} "
                  f"a la altura {altura:.4f}")

            # Cómo se calcula la distancia del grupo nuevo a cada grupo que queda.
            actualizaciones = []
            ia, ib = paso["grupos"].index(a), paso["grupos"].index(b)
            for t, x in enumerate(paso["grupos"]):
                if x in (a, b):
                    continue
                d_ax, d_bx = paso["matriz"][ia][t], paso["matriz"][ib][t]
                d = cl.distancia_nueva(criterio, d_ax, d_bx, tam[a], tam[b])
                if criterio == "single":
                    formula = f"min({d_ax:.4f}, {d_bx:.4f}) = {d:.4f}"
                elif criterio == "complete":
                    formula = f"max({d_ax:.4f}, {d_bx:.4f}) = {d:.4f}"
                else:
                    formula = (f"({tam[a]}·{d_ax:.4f} + {tam[b]}·{d_bx:.4f}) / "
                               f"{tam[a] + tam[b]} = {d:.4f}")
                print(f"   d({nombre_grupo(nuevo, m, CASO)}, {nombre_grupo(x, m, CASO)}) = {formula}")
                actualizaciones.append({"con": nombre_grupo(x, m, CASO), "d_a": d_ax,
                                        "d_b": d_bx, "resultado": d, "formula": formula})
            pasos_json.append({"grupos": nombres, "matriz": paso["matriz"],
                               "une": [nombre_grupo(a, m, CASO), nombre_grupo(b, m, CASO)],
                               "altura": altura, "nuevo": nombre_grupo(nuevo, m, CASO),
                               "actualizaciones": actualizaciones})

        C = cl.matriz_cofenetica(uniones, n)
        r = cl.correlacion_cofenetica(D, C)
        imprimir_matriz("\nMatriz cofenética", [str(x) for x in CASO], C)
        print(f"Correlación cofenética ({n * (n - 1) // 2} pares): {r:.4f}")
        salida["criterios"][criterio] = {"pasos": pasos_json, "uniones": uniones,
                                         "cofenetica": C, "correlacion": r}

    # Los tres dendrogramas del caso en una sola figura.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ejes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, criterio in zip(ejes, cl.CRITERIOS):
        datos = salida["criterios"][criterio]
        uniones = datos["uniones"]
        for xs, ys in cl.coordenadas_dendrograma(uniones, n):
            ax.plot(xs, ys, color="#1f4e79", linewidth=1.6)
        orden = cl.orden_hojas(uniones, n)
        ax.set_xticks(range(n))
        ax.set_xticklabels([str(CASO[i]) for i in orden])
        ax.set_title(f"{criterio.capitalize()} (r = {datos['correlacion']:.4f})")
        ax.set_xlabel("Artículo")
        ax.spines[["top", "right"]].set_visible(False)
    ejes[0].set_ylabel("Distancia")
    ejes[0].set_ylim(0.75, 1.02)
    fig.tight_layout()
    fig.savefig(RESULTADOS / "req2_caso_dendrogramas.png", dpi=150)
    plt.close(fig)

    (RESULTADOS / "req2_caso_estudio.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nGuardado en resultados/req2_caso_estudio.json y resultados/req2_caso_dendrogramas.png")


if __name__ == "__main__":
    main()