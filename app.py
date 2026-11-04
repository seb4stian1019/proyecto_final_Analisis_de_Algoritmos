"""
REQUERIMIENTO 4 - Aplicación web del proyecto (Streamlit)
=========================================================
Interfaz para usar los tres requerimientos desde el navegador. La aplicación NO
reprograma ningún algoritmo: solo llama a las funciones de los módulos del
proyecto y muestra sus resultados.

  Corpus  -> paso1_corpus/datos.py          (título, autores y abstract de los 20 PDF)
  Req 1   -> req1_similitud/comparar.py      (6 algoritmos de similitud sobre los artículos elegidos)
  Req 2   -> req2_agrupamiento/clustering.py (3 criterios de agrupamiento, dendrograma y cofenética)
  Req 3   -> req3_busqueda/buscar_patron.py  (KMP, Boyer-Moore y Rabin-Karp sobre los 20 abstracts)

Los vectores de los modelos de IA se leen de resultados/req1_embeddings.json, así que
la aplicación no necesita instalar ni descargar los modelos.

Uso local:  streamlit run app.py
"""

import time

import matplotlib
import streamlit as st

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from req2_agrupamiento import clustering as cl  # noqa: E402
from paso1_corpus.datos import cargar_corpus  # noqa: E402
from req1_similitud.comparar import NOMBRES, Comparador  # noqa: E402
from req3_busqueda.buscar_patron import ALGORITMOS, buscar_en_corpus, contexto  # noqa: E402

st.set_page_config(page_title="Bibliometría · Análisis de Algoritmos", layout="wide")


# ---------------------------------------------------------------- datos (una sola vez)
@st.cache_resource
def preparar():
    corpus = cargar_corpus()
    return corpus, Comparador(corpus), cl.matriz_distancias([a["abstract"] for a in corpus])


corpus, comparador, D = preparar()
por_id = {a["id"]: a for a in corpus}
ids = [a["id"] for a in corpus]


def etiqueta(i):
    titulo = por_id[i]["titulo"]
    return f"{i}. {titulo[:80]}{'…' if len(titulo) > 80 else ''}"


st.title("Análisis de algoritmos en el contexto de la bibliometría")
st.caption("Proyecto final 2026-2 · Universidad del Quindío · Samuel Salgado Figueroa y Sebastián Amaya Castaño. "
           "Todos los algoritmos están programados a mano; el código está en el repositorio.")

tab0, tab1, tab2, tab3 = st.tabs(["Corpus", "Req 1 · Similitud", "Req 2 · Agrupamiento", "Req 3 · Búsqueda"])

# ---------------------------------------------------------------- corpus
with tab0:
    st.subheader("Los 20 artículos del corpus")
    st.write("Título, autores y abstract extraídos de cada PDF por paso1_corpus/extraer.py y verificados "
             "con paso1_corpus/verificar.py.")
    st.dataframe([{"N.º": a["id"], "Título": a["titulo"], "Autores": ", ".join(a["autores"]),
                   "Palabras del abstract": len(a["abstract"].split())} for a in corpus],
                 hide_index=True, width="stretch")
    elegido = st.selectbox("Ver el abstract de un artículo", ids, format_func=etiqueta)
    st.write(por_id[elegido]["abstract"])

# ---------------------------------------------------------------- Req 1
with tab1:
    st.subheader("Similitud textual entre dos o más abstracts")
    st.write("Cuatro algoritmos clásicos (Levenshtein, LCS, Jaccard y coseno con TF-IDF) y dos modelos de IA "
             "(GloVe y MiniLM). Todos los valores van de 0 (nada en común) a 1 (iguales).")
    elegidos = st.multiselect("Elige dos o más artículos", ids, default=[11, 16], format_func=etiqueta)
    if len(elegidos) < 2:
        st.info("Elige al menos dos artículos.")
    else:
        elegidos = sorted(elegidos)
        filas = []
        inicio = time.perf_counter()
        for x in range(len(elegidos)):
            for y in range(x + 1, len(elegidos)):
                valores = comparador.comparar(elegidos[x], elegidos[y])
                filas.append({"Par": f"{elegidos[x]} – {elegidos[y]}", **{n: round(valores[n], 4) for n in NOMBRES}})
        st.dataframe(filas, hide_index=True, width="stretch")
        st.caption(f"{len(filas)} pares comparados en {(time.perf_counter() - inicio) * 1000:.1f} ms.")
        if len(filas) == 1:
            fig, ax = plt.subplots(figsize=(7, 3))
            ax.barh(NOMBRES[::-1], [filas[0][n] for n in NOMBRES[::-1]], color="#1f4e79")
            ax.set_xlim(0, 1)
            ax.set_xlabel("Similitud")
            ax.spines[["top", "right"]].set_visible(False)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

# ---------------------------------------------------------------- Req 2
with tab2:
    st.subheader("Agrupamiento jerárquico de los 20 abstracts")
    st.write("Distancia = 1 − coseno TF-IDF. Agrupamiento aglomerativo programado en req2_agrupamiento/clustering.py y evaluado con "
             "el coeficiente de correlación cofenética (más cerca de 1 = el árbol conserva mejor las distancias).")
    nombres = {"single": "Single linkage", "complete": "Complete linkage", "average": "Average linkage"}
    resumen = []
    arboles = {}
    for criterio in cl.CRITERIOS:
        uniones = cl.agrupar(D, criterio)
        arboles[criterio] = uniones
        resumen.append({"Criterio": nombres[criterio],
                        "Correlación cofenética": round(cl.correlacion_cofenetica(D, cl.matriz_cofenetica(uniones, len(D))), 4),
                        "Altura de la raíz": round(uniones[-1][2], 4)})
    st.dataframe(resumen, hide_index=True, width="stretch")
    mejor = max(resumen, key=lambda r: r["Correlación cofenética"])
    st.success(f"Criterio con la correlación cofenética más alta: {mejor['Criterio']} "
               f"({mejor['Correlación cofenética']}).")

    col1, col2 = st.columns([1, 1])
    criterio = col1.radio("Criterio del dendrograma", cl.CRITERIOS, format_func=lambda c: nombres[c], horizontal=True)
    k = col2.slider("Cortar el árbol en k grupos", 2, 8, 4)
    uniones = arboles[criterio]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for xs, ys in cl.coordenadas_dendrograma(uniones, len(D)):
        ax.plot(xs, ys, color="#1f4e79", linewidth=1.4)
    orden = cl.orden_hojas(uniones, len(D))
    ax.set_xticks(range(len(D)))
    ax.set_xticklabels([str(ids[i]) for i in orden])
    ax.set_xlabel("Artículo")
    ax.set_ylabel("Distancia (1 − coseno TF-IDF)")
    ax.set_ylim(min(u[2] for u in uniones) - 0.1, max(u[2] for u in uniones) + 0.02)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.markdown(f"**Grupos al cortar en {k}:**")
    for n_grupo, grupo in enumerate(cl.cortar(uniones, len(D), k), start=1):
        st.markdown(f"- Grupo {n_grupo}: " + "; ".join(etiqueta(ids[i]) for i in grupo))

# ---------------------------------------------------------------- Req 3
with tab3:
    st.subheader("Búsqueda de un patrón en los 20 abstracts")
    st.write("KMP, Boyer-Moore y Rabin-Karp programados sin find() ni index(). La búsqueda no distingue mayúsculas "
             "de minúsculas, y se verifica que los tres encuentren las mismas posiciones que la fuerza bruta.")
    patron = st.text_input("Patrón a buscar", value="generative ai")
    if patron.strip():
        inicio = time.perf_counter()
        filas = buscar_en_corpus(patron, corpus)
        ms = (time.perf_counter() - inicio) * 1000
        total = sum(len(f["posiciones"]) for f in filas)
        con = [f for f in filas if f["posiciones"]]
        st.write(f"**{total} ocurrencias** en {len(con)} de {len(filas)} artículos "
                 f"(búsqueda con los tres algoritmos y la verificación: {ms:.1f} ms).")
        st.dataframe([{"Algoritmo": n, "Comparaciones de caracteres en el corpus": sum(f[n] for f in filas)}
                      for n in ALGORITMOS], hide_index=True, width="stretch")
        st.caption("Rabin-Karp solo compara caracteres cuando el hash coincide; su trabajo principal es actualizar "
                   "el hash de cada ventana del texto.")
        for f in con:
            with st.expander(f"{etiqueta(f['id'])} · {len(f['posiciones'])} ocurrencia(s)"):
                st.write(f"Posiciones: {f['posiciones']}")
                st.write(f"«{contexto(por_id[f['id']]['abstract'], f['posiciones'][0], len(patron))}»")