"""
REQUERIMIENTO 4 - Aplicación web del proyecto (Streamlit)
=========================================================
La aplicación NO reprograma ningún algoritmo: solo llama a las funciones de los
módulos del proyecto y muestra sus resultados en cinco pestañas.

  Inicio        -> resumen del proyecto
  Corpus        -> paso1_corpus/datos.py          (los 20 artículos)
  Similitud     -> req1_similitud/comparar.py      (6 algoritmos)
  Agrupamiento  -> req2_agrupamiento/clustering.py (3 criterios y dendrograma)
  Búsqueda      -> req3_busqueda/buscar_patron.py  (KMP, Boyer-Moore y Rabin-Karp)

No hace falta correr nada antes: el corpus y los vectores de IA ya están guardados en
resultados/, y lo demás se calcula al abrir la página. Los colores de la página están
en .streamlit/config.toml.

Uso local:  python -m streamlit run app.py
"""

import time

import matplotlib
import streamlit as st

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from paso1_corpus.datos import cargar_corpus  # noqa: E402
from req1_similitud.comparar import NOMBRES, Comparador  # noqa: E402
from req2_agrupamiento import clustering as cl  # noqa: E402
from req3_busqueda.buscar_patron import ALGORITMOS, buscar_en_corpus  # noqa: E402

REPO = "https://github.com/seb4stian1019/proyecto_final_Analisis_de_Algoritmos"
CRITERIOS = {"single": "Single linkage", "complete": "Complete linkage", "average": "Average linkage"}
COLORES = [("azul", "#2a78d6"), ("naranja", "#eb6834"), ("verde", "#1baf7a"), ("amarillo", "#eda100"),
           ("rosado", "#e87ba4"), ("verde oscuro", "#008300"), ("morado", "#6250d6"), ("rojo", "#e34948")]

st.set_page_config(page_title="Bibliometría · Análisis de Algoritmos", page_icon="📚", layout="wide")


# ------------------------------------------------------------------ datos
# Se calculan una sola vez y quedan en memoria (caché) para todas las visitas.
@st.cache_resource
def preparar():
    corpus = cargar_corpus()
    comparador = Comparador(corpus)                                    # Req 1
    D = cl.matriz_distancias([a["abstract"] for a in corpus])          # Req 2
    arboles = {c: cl.agrupar(D, c) for c in CRITERIOS}
    cofenetica = {c: cl.correlacion_cofenetica(D, cl.matriz_cofenetica(arboles[c], len(D))) for c in CRITERIOS}
    return corpus, comparador, D, arboles, cofenetica


corpus, comparador, D, arboles, cofenetica = preparar()
por_id = {a["id"]: a for a in corpus}
ids = list(por_id)
mejor = max(cofenetica, key=cofenetica.get)


def nombre(i):
    """'11. A scoping review on how generative…' para las listas desplegables."""
    t = por_id[i]["titulo"]
    return f"{i}. {t[:75]}…" if len(t) > 75 else f"{i}. {t}"


def resaltar(texto, posiciones, largo):
    """Devuelve el abstract con cada ocurrencia del patrón sobre fondo naranja (formato de Streamlit)."""
    def escapar(s):                     # para que *, _, $… del abstract no se tomen como formato
        return "".join("\\" + c if c in "\\`*_[]$#" else c for c in s)
    partes, ultimo = [], 0
    for p in posiciones:
        if p >= ultimo:                 # si dos ocurrencias se solapan, se marca la primera
            partes += [escapar(texto[ultimo:p]), f":orange-background[{escapar(texto[p:p + largo])}]"]
            ultimo = p + largo
    return "".join(partes) + escapar(texto[ultimo:])


# ------------------------------------------------------------------ encabezado
with st.sidebar:
    st.header("📚 Proyecto final")
    st.markdown("**Análisis de Algoritmos 2026-2**  \nUniversidad del Quindío")
    st.markdown("**Autores**  \nSamuel Salgado Figueroa  \nSebastián Amaya Castaño")
    st.markdown("**Docente**  \nSergio Augusto Cardona Torres")
    st.link_button("Ver el código en GitHub", REPO)

st.title("Análisis de algoritmos en el contexto de la bibliometría")
st.write("Similitud textual, agrupamiento jerárquico y búsqueda de patrones sobre los abstracts de 20 artículos "
         "científicos sobre inteligencia artificial en la educación. Todos los algoritmos están programados a mano "
         "y esta página ejecuta el mismo código del repositorio.")

inicio, tab_corpus, tab_sim, tab_grupos, tab_busqueda = st.tabs(
    ["🏠 Inicio", "📄 Corpus", "🔗 Req 1 · Similitud", "🌳 Req 2 · Agrupamiento", "🔍 Req 3 · Búsqueda"])

# ------------------------------------------------------------------ Inicio
with inicio:
    c = st.columns(4)
    c[0].metric("Artículos", len(corpus), border=True)
    c[1].metric("Algoritmos de similitud", len(NOMBRES), border=True)
    c[2].metric("Criterios de agrupamiento", len(CRITERIOS), border=True)
    c[3].metric("Algoritmos de búsqueda", len(ALGORITMOS), border=True)

    caso = comparador.comparar(11, 16)
    st.markdown(f"""
| Requerimiento | Qué hace | Resultado principal |
|---|---|---|
| **Req 1 · Similitud** | Compara abstracts con Levenshtein, LCS, Jaccard, coseno TF-IDF, GloVe y MiniLM | Artículos 11 y 16: coseno TF-IDF {caso['Coseno TF-IDF']:.4f}, MiniLM {caso['MiniLM']:.4f} |
| **Req 2 · Agrupamiento** | Agrupa los 20 abstracts con single, complete y average linkage | Mejor criterio: {CRITERIOS[mejor]}, correlación cofenética {cofenetica[mejor]:.4f} |
| **Req 3 · Búsqueda** | Busca un patrón con KMP, Boyer-Moore y Rabin-Karp | Los tres encuentran las mismas posiciones que la fuerza bruta |
| **Req 4 · Aplicación** | Esta página, desplegada en Streamlit Community Cloud | Usa las funciones de los requerimientos 1, 2 y 3 |
""")

# ------------------------------------------------------------------ Corpus
with tab_corpus:
    st.subheader("Los 20 artículos del corpus")
    st.caption("Extraídos de los PDF con paso1_corpus/extraer.py y verificados con paso1_corpus/verificar.py.")
    st.dataframe([{"N.º": a["id"], "Título": a["titulo"], "Autores": ", ".join(a["autores"]),
                   "Palabras": a["palabras"]} for a in corpus], hide_index=True, height=738)
    elegido = st.selectbox("Leer un abstract", ids, format_func=nombre)
    with st.container(border=True):
        st.markdown(f"**{por_id[elegido]['titulo']}**")
        st.caption(", ".join(por_id[elegido]["autores"]))
        st.write(por_id[elegido]["abstract"])

# ------------------------------------------------------------------ Req 1
with tab_sim:
    st.subheader("Similitud entre abstracts")
    st.caption("Valores de 0 (nada en común) a 1 (iguales). Código: req1_similitud/similitud.py.")
    elegidos = sorted(st.multiselect("Elija dos o más artículos", ids, default=[11, 16], format_func=nombre))

    if len(elegidos) < 2:
        st.info("Elija al menos dos artículos.")
    else:
        pares = [(a, b) for k, a in enumerate(elegidos) for b in elegidos[k + 1:]]
        inicio_t = time.perf_counter()
        valores = {par: comparador.comparar(*par) for par in pares}          # aquí corren los 6 algoritmos
        ms = (time.perf_counter() - inicio_t) * 1000

        if len(pares) == 1:                         # un par: una tarjeta por algoritmo y una gráfica
            v = valores[pares[0]]
            c = st.columns(6)
            for col, n in zip(c, NOMBRES):
                col.metric(n, f"{v[n]:.4f}", border=True)
            st.bar_chart({"Algoritmo": NOMBRES,
                          "Clásicos": [v[n] if n in NOMBRES[:4] else None for n in NOMBRES],
                          "Con IA": [v[n] if n in NOMBRES[4:] else None for n in NOMBRES]},
                         x="Algoritmo", y=["Clásicos", "Con IA"], color=["#2a78d6", "#eb6834"],
                         horizontal=True, sort=False, y_label="Similitud")
        else:                                       # varios pares: una fila por par
            st.dataframe([{"Par": f"{a} – {b}", **{n: round(valores[(a, b)][n], 4) for n in NOMBRES}}
                          for a, b in pares], hide_index=True)
        st.caption(f"{len(pares)} par(es) comparados con los 6 algoritmos en {ms:.1f} ms.")

# ------------------------------------------------------------------ Req 2
with tab_grupos:
    st.subheader("Agrupamiento jerárquico de los 20 abstracts")
    st.caption("Distancia = 1 − coseno TF-IDF. La correlación cofenética mide qué tan bien conserva el árbol las "
               "distancias reales: más cerca de 1 es mejor. Código: req2_agrupamiento/clustering.py.")
    c = st.columns(3)
    for col, criterio in zip(c, CRITERIOS):
        col.metric(CRITERIOS[criterio], f"{cofenetica[criterio]:.4f}",
                   "mejor" if criterio == mejor else None, border=True)

    c1, c2 = st.columns(2)
    criterio = c1.radio("Criterio", list(CRITERIOS), index=list(CRITERIOS).index(mejor),
                        format_func=CRITERIOS.get, horizontal=True)
    k = c2.slider("Cortar el árbol en k grupos", 2, 8, 4)

    # Dendrograma: las coordenadas las calcula clustering.py; matplotlib solo dibuja.
    # Cada grupo del corte va de un color; las uniones por encima del corte, en gris.
    n = len(D)
    uniones = arboles[criterio]
    grupos = cl.cortar(uniones, n, k)
    color_de = {hoja: COLORES[g][1] for g, grupo in enumerate(grupos) for hoja in grupo}
    miembros = cl.miembros(uniones, n)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for t, (xs, ys) in enumerate(cl.coordenadas_dendrograma(uniones, n)):
        colores = {color_de[h] for h in miembros[n + t]}
        ax.plot(xs, ys, color=colores.pop() if len(colores) == 1 else "#a3a8b0", linewidth=1.8)
    ax.set_xticks(range(n), [str(ids[h]) for h in cl.orden_hojas(uniones, n)])
    ax.set_ylim(min(u[2] for u in uniones) - 0.05, uniones[-1][2] + 0.015)
    ax.set_xlabel("Artículo")
    ax.set_ylabel("Distancia")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    for g, grupo in enumerate(grupos):
        st.markdown(f"**Grupo {g + 1}** ({COLORES[g][0]}, {len(grupo)} artículo(s)): "
                    + ", ".join(str(ids[h]) for h in grupo))

# ------------------------------------------------------------------ Req 3
with tab_busqueda:
    st.subheader("Búsqueda de un patrón en los 20 abstracts")
    st.caption("No distingue mayúsculas de minúsculas. Código: req3_busqueda/busqueda.py.")
    patron = st.text_input("Palabra o frase a buscar", value="generative ai")

    if patron.strip():
        inicio_t = time.perf_counter()
        filas = buscar_en_corpus(patron, corpus)          # corre KMP, Boyer-Moore y Rabin-Karp y los verifica
        ms = (time.perf_counter() - inicio_t) * 1000
        con = [f for f in filas if f["posiciones"]]

        c = st.columns(3)
        c[0].metric("Ocurrencias", sum(len(f["posiciones"]) for f in con), border=True)
        c[1].metric("Artículos donde aparece", f"{len(con)} de {len(filas)}", border=True)
        c[2].metric("Tiempo", f"{ms:.1f} ms", border=True)
        st.bar_chart({"Algoritmo": list(ALGORITMOS), "Comparaciones": [sum(f[a] for f in filas) for a in ALGORITMOS]},
                     x="Algoritmo", y="Comparaciones", horizontal=True, sort=False,
                     y_label="Comparaciones de caracteres")
        st.caption("Rabin-Karp casi no compara caracteres: compara hashes y solo revisa letra por letra cuando coinciden.")

        if not con:
            st.info("El patrón no aparece en ningún abstract.")
        for f in con:
            with st.expander(f"{nombre(f['id'])} · {len(f['posiciones'])} ocurrencia(s)"):
                st.markdown(resaltar(por_id[f["id"]]["abstract"], f["posiciones"], len(patron)))