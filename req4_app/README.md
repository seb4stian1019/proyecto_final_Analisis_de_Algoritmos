# Requerimiento 4: aplicación desplegada

La aplicación web permite usar los tres requerimientos desde el navegador, sin instalar nada. Está hecha con Streamlit y su código es un solo archivo, `app.py`, en la raíz del proyecto.

**Enlace:** se agrega cuando la aplicación esté desplegada en Streamlit Community Cloud.

## Qué hace cada pestaña

| Pestaña | Qué permite hacer | Módulo que usa |
|---|---|---|
| Corpus | Ver los 20 artículos con su título, autores y abstract | `paso1_corpus/datos.py` |
| Req 1 · Similitud | Elegir dos o más artículos y comparar cada par con los 6 algoritmos | `req1_similitud/comparar.py` |
| Req 2 · Agrupamiento | Ver la correlación cofenética de los 3 criterios, el dendrograma de cada uno y los grupos al cortar el árbol en k | `req2_agrupamiento/clustering.py` |
| Req 3 · Búsqueda | Escribir un patrón y buscarlo en los 20 abstracts con KMP, Boyer-Moore y Rabin-Karp | `req3_busqueda/buscar_patron.py` |

## Arquitectura

La aplicación es solo la capa de presentación. No reprograma ningún algoritmo: llama a las mismas funciones que usan los scripts y `main.py`, de modo que lo que se ve en la página es exactamente lo que está documentado.

```
Navegador ──> app.py (Streamlit: pestañas, controles y gráficas)
                 │
                 ├── paso1_corpus/datos.py ────────> resultados/corpus.json
                 ├── req1_similitud/comparar.py ───> similitud.py + resultados/req1_embeddings.json
                 ├── req2_agrupamiento/clustering.py
                 └── req3_busqueda/buscar_patron.py ─> busqueda.py
```

- El corpus y los vectores de los modelos de IA se leen de `resultados/`, que está en el repositorio. Por eso la aplicación no necesita los PDF ni instalar los modelos de IA.
- Lo que se calcula una sola vez (corpus, idf y matriz de distancias) queda en caché con `st.cache_resource`; cada interacción solo ejecuta el algoritmo que corresponde.
- matplotlib solo dibuja: las coordenadas del dendrograma las calcula `clustering.py`.

## Cómo ejecutarla en el computador

Desde la raíz del proyecto:

```
pip install -r requirements.txt
python -m streamlit run app.py
```

Se abre en el navegador en http://localhost:8501.

## Cómo se desplegó

1. Entrar a https://share.streamlit.io con la cuenta de GitHub.
2. **Create app** → repositorio `seb4stian1019/proyecto_final_Analisis_de_Algoritmos`, rama `main`, archivo principal `app.py`.
3. **Deploy**. Streamlit Community Cloud instala `requirements.txt` y publica la aplicación. Cada vez que se fusiona un cambio en `main`, la aplicación se actualiza sola.