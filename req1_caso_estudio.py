"""
REQUERIMIENTO 1 - Caso de estudio paso a paso
==============================================
El enunciado pide elegir dos abstracts y mostrar, paso a paso, cómo funciona
matemáticamente cada algoritmo, y comparar los resultados clásicos con los de IA.

Caso elegido: artículos 11 y 16. Los dos tratan el mismo tema (cómo la IA
generativa cambia la evaluación en la educación superior), pero con palabras
distintas ("higher education" frente a "tertiary education"). Es un buen caso
para ver qué algoritmos detectan el parecido de tema y cuáles no.

Para que las matrices de programación dinámica se puedan mostrar completas, la
demostración de Levenshtein y LCS usa la PRIMERA ORACIÓN de cada abstract. Los
valores finales se calculan con los abstracts completos.

Salida: resultados/req1_caso_estudio.json y resultados/req1_grafico_caso.png
Uso:    python req1_caso_estudio.py
"""

import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import similitud as s
from datos import RESULTADOS, cargar_corpus
from req1_similitud import NOMBRES, Comparador

A, B = 11, 16
DIMENSIONES_MOSTRADAS = 5           # primeras componentes de los vectores densos que se imprimen


def primera_oracion(texto):
    """Texto hasta el primer punto seguido de espacio (recorrido carácter a carácter)."""
    for k in range(len(texto) - 1):
        if texto[k] == "." and texto[k + 1] == " ":
            return texto[:k + 1]
    return texto


def imprimir_matriz(titulo, a, b, M):
    print(f"\n{titulo}")
    print(" " * 14 + "".join(f"{p[:6]:>7}" for p in [""] + b))
    for i in range(len(a) + 1):
        etiqueta = "" if i == 0 else a[i - 1][:12]
        print(f"{etiqueta:>14}" + "".join(f"{M[i][j]:>7}" for j in range(len(b) + 1)))


def angulo(cos):
    """Ángulo en grados entre dos vectores a partir de su coseno."""
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def main():
    corpus = cargar_corpus()
    articulos = {a["id"]: a for a in corpus}
    comparador = Comparador(corpus)
    pa, pb = comparador.palabras[A], comparador.palabras[B]
    caso = {"articulos": {str(i): articulos[i]["titulo"] for i in (A, B)}}

    print(f"Artículo {A}: {articulos[A]['titulo']}")
    print(f"Artículo {B}: {articulos[B]['titulo']}")
    print(f"Palabras después del preprocesamiento: {len(pa)} y {len(pb)}")

    # ---- 1 y 2. Programación dinámica con la primera oración ----
    oa = s.preprocesar(primera_oracion(articulos[A]["abstract"]))
    ob = s.preprocesar(primera_oracion(articulos[B]["abstract"]))
    D = s.matriz_levenshtein(oa, ob)
    L = s.matriz_lcs(oa, ob)
    comun_oracion = s.reconstruir_lcs(oa, ob, L)
    imprimir_matriz("Levenshtein (primera oración): D[i][j]", oa, ob, D)
    print(f"Distancia = D[{len(oa)}][{len(ob)}] = {D[len(oa)][len(ob)]}")
    imprimir_matriz("LCS (primera oración): L[i][j]", oa, ob, L)
    print(f"LCS = {comun_oracion} (largo {len(comun_oracion)})")

    distancia = s.levenshtein(pa, pb)
    L_total = s.matriz_lcs(pa, pb)
    comun_total = s.reconstruir_lcs(pa, pb, L_total)
    print(f"\nAbstracts completos: distancia de Levenshtein = {distancia}, "
          f"similitud = 1 - {distancia}/{max(len(pa), len(pb))}")
    print(f"LCS completa ({len(comun_total)} palabras): {' '.join(comun_total)}")
    caso["programacion_dinamica"] = {
        "oracion_a": oa, "oracion_b": ob, "matriz_levenshtein": D, "matriz_lcs": L,
        "lcs_oracion": comun_oracion,
        "palabras_a": len(pa), "palabras_b": len(pb), "distancia_completa": distancia,
        "lcs_completa": comun_total,
    }

    # ---- 3. Jaccard ----
    conj_a, conj_b = set(pa), set(pb)
    interseccion = sorted(conj_a & conj_b)
    union = conj_a | conj_b
    print(f"\nJaccard: |A| = {len(conj_a)}, |B| = {len(conj_b)}, |A ∩ B| = {len(interseccion)}, "
          f"|A ∪ B| = {len(union)}")
    print(f"  palabras en común: {', '.join(interseccion)}")
    caso["jaccard"] = {"A": len(conj_a), "B": len(conj_b), "interseccion": interseccion, "union": len(union)}

    # ---- 4. TF-IDF y coseno ----
    idf = comparador.tfidf.idf
    va, vb = comparador.tfidf.vector(pa), comparador.tfidf.vector(pb)
    fa, fb = s.frecuencias(pa), s.frecuencias(pb)
    conjuntos = [set(p) for p in comparador.palabras.values()]
    df = {t: sum(1 for c in conjuntos if t in c) for t in interseccion}     # en cuántos abstracts está t
    filas = []
    for t in sorted(interseccion, key=lambda t: -va[t] * vb[t]):
        filas.append({"palabra": t, "veces_a": fa[t], "veces_b": fb[t], "df": df[t], "idf": idf[t],
                      "peso_a": va[t], "peso_b": vb[t], "producto": va[t] * vb[t]})
    producto = sum(f["producto"] for f in filas)
    norma_a = math.sqrt(sum(p * p for p in va.values()))
    norma_b = math.sqrt(sum(p * p for p in vb.values()))
    cos_tfidf = producto / (norma_a * norma_b)
    print(f"\nTF-IDF (N = {len(corpus)}): palabras en común ordenadas por aporte al producto punto")
    print(f"{'palabra':<14}{'tf A':>5}{'tf B':>5}{'df':>4}{'idf':>8}{'peso A':>9}{'peso B':>9}{'A·B':>10}")
    for f in filas:
        print(f"{f['palabra']:<14}{f['veces_a']:>5}{f['veces_b']:>5}{f['df']:>4}{f['idf']:>8.4f}"
              f"{f['peso_a']:>9.5f}{f['peso_b']:>9.5f}{f['producto']:>10.6f}")
    print(f"u·v = {producto:.6f}   |u| = {norma_a:.5f}   |v| = {norma_b:.5f}")
    print(f"cos = {producto:.6f} / ({norma_a:.5f} · {norma_b:.5f}) = {cos_tfidf:.4f}  "
          f"-> ángulo = {angulo(cos_tfidf):.1f}°")
    caso["tfidf"] = {"filas": filas, "producto": producto, "norma_a": norma_a, "norma_b": norma_b,
                     "coseno": cos_tfidf, "angulo": angulo(cos_tfidf)}

    # ---- 5 y 6. Modelos de IA ----
    caso["ia"] = {}
    for clave, vectores in (("GloVe", comparador.glove), ("MiniLM", comparador.minilm)):
        u, v = vectores[str(A)], vectores[str(B)]
        prod = sum(u[k] * v[k] for k in range(len(u)))
        nu, nv = math.sqrt(sum(x * x for x in u)), math.sqrt(sum(x * x for x in v))
        cos = s.coseno_listas(u, v)
        print(f"\n{clave}: {len(u)} dimensiones")
        print(f"  u = [{', '.join(f'{x:.4f}' for x in u[:DIMENSIONES_MOSTRADAS])}, ...]")
        print(f"  v = [{', '.join(f'{x:.4f}' for x in v[:DIMENSIONES_MOSTRADAS])}, ...]")
        print(f"  u·v = {prod:.4f}   |u| = {nu:.4f}   |v| = {nv:.4f}   cos = {cos:.4f}  "
              f"-> ángulo = {angulo(cos):.1f}°")
        caso["ia"][clave] = {"dimensiones": len(u), "u": u[:DIMENSIONES_MOSTRADAS], "v": v[:DIMENSIONES_MOSTRADAS],
                             "producto": prod, "norma_u": nu, "norma_v": nv, "coseno": cos, "angulo": angulo(cos)}

    # ---- Resumen y comparación con el resto del corpus ----
    valores = comparador.comparar(A, B)
    print(f"\nResumen del caso {A}-{B} y posición del artículo {B} entre los 19 artículos comparados con el {A}:")
    caso["resumen"] = {}
    for n in NOMBRES:
        otros = sorted(((comparador.comparar(A, j)[n], j) for j in articulos if j != A), reverse=True)
        puesto = [j for _, j in otros].index(B) + 1
        print(f"  {n:<14}{valores[n]:8.4f}   puesto {puesto:>2} de 19")
        caso["resumen"][n] = {"similitud": valores[n], "puesto": puesto}

    fig, eje = plt.subplots(figsize=(7, 3.6), dpi=150)
    colores = ["#2E5597"] * 4 + ["#C55A11"] * 2
    barras = eje.bar(NOMBRES, [valores[n] for n in NOMBRES], color=colores)
    for barra, n in zip(barras, NOMBRES):
        eje.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.02,
                 f"{valores[n]:.3f}".replace(".", ","), ha="center", fontsize=8)
    eje.set_ylim(0, 1.1)
    eje.set_ylabel("Similitud")
    eje.set_title(f"Similitud entre los artículos {A} y {B} (azul: clásicos; naranja: IA)", fontsize=10)
    eje.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTADOS / "req1_grafico_caso.png")
    plt.close(fig)

    (RESULTADOS / "req1_caso_estudio.json").write_text(json.dumps(caso, ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
    print("\nCaso guardado en resultados/req1_caso_estudio.json y resultados/req1_grafico_caso.png")


if __name__ == "__main__":
    main()
