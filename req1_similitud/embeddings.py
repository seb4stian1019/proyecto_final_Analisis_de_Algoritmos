"""
REQUERIMIENTO 1 - Vectores (embeddings) de los 20 abstracts con dos modelos de IA
=================================================================================
El enunciado permite usar modelos preentrenados para VECTORIZAR los abstracts.
La similitud entre los vectores (coseno) se calcula a mano en similitud.py.

Modelo 1 - GloVe (Pennington et al., 2014), 50 dimensiones.
    Es un diccionario fijo: a cada palabra le corresponde un vector de 50 números,
    aprendido de Wikipedia. El vector del abstract es el PROMEDIO de los vectores
    de sus palabras (el promedio lo calculamos nosotros). No tiene en cuenta el
    orden ni el contexto de las palabras.

Modelo 2 - all-MiniLM-L6-v2 (Sentence-BERT; Reimers y Gurevych, 2019), 384 dimensiones.
    Es una red neuronal tipo transformer: lee el abstract completo y produce un solo
    vector para todo el texto, teniendo en cuenta el contexto de cada palabra.

Los vectores se calculan UNA vez y se guardan en resultados/req1_embeddings.json.
Así, el resto del proyecto (y la aplicación web) no necesita los modelos.

Instalación (solo para este script):  pip install -r requirements-ia.txt
Uso:                                  python -m req1_similitud.embeddings
La primera vez descarga los modelos (GloVe ~66 MB, MiniLM ~90 MB) en la carpeta modelos/.
"""

import gzip
import json
import urllib.request

from paso1_corpus.datos importBASE, RESULTADOS, cargar_corpus
from req1_similitud.similitud import preprocesar

MODELOS = BASE / "modelos"
URL_GLOVE = ("https://github.com/RaRe-Technologies/gensim-data/releases/download/"
             "glove-wiki-gigaword-50/glove-wiki-gigaword-50.gz")
ARCHIVO_GLOVE = MODELOS / "glove-wiki-gigaword-50.gz"
NOMBRE_MINILM = "sentence-transformers/all-MiniLM-L6-v2"


# ===========================================================================
# Modelo 1: GloVe (promedio de vectores de palabras)
# ===========================================================================
def cargar_glove(vocabulario):
    """Lee el archivo de GloVe línea por línea: 'palabra n1 n2 ... n50'.
    Solo guarda las palabras que aparecen en el corpus (el archivo trae 400.000)."""
    if not ARCHIVO_GLOVE.exists():
        MODELOS.mkdir(exist_ok=True)
        print(f"Descargando GloVe (~66 MB) en {ARCHIVO_GLOVE} ...")
        urllib.request.urlretrieve(URL_GLOVE, ARCHIVO_GLOVE)
    vectores = {}
    with gzip.open(ARCHIVO_GLOVE, "rt", encoding="utf-8") as f:
        next(f)                                     # primera línea: "400000 50"
        for linea in f:
            partes = linea.rstrip().split(" ")
            if partes[0] in vocabulario:
                vectores[partes[0]] = [float(x) for x in partes[1:]]
    return vectores


def promedio_glove(palabras, vectores):
    """Vector del abstract = suma de los vectores de sus palabras / cantidad de palabras.
    Las palabras que GloVe no conoce se omiten (y se cuentan)."""
    conocidas = [p for p in palabras if p in vectores]
    dim = len(next(iter(vectores.values())))
    suma = [0.0] * dim
    for p in conocidas:
        for k in range(dim):
            suma[k] += vectores[p][k]
    return [x / len(conocidas) for x in suma], len(conocidas)


# ===========================================================================
# Modelo 2: MiniLM (un vector por abstract completo)
# ===========================================================================
def vectores_minilm(textos):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise SystemExit("Falta la librería del modelo 2. Instálela con:  "
                         "python -m pip install -r requirements-ia.txt")
    modelo = SentenceTransformer(NOMBRE_MINILM, cache_folder=str(MODELOS))
    # El modelo recibe el abstract tal cual (con mayúsculas y palabras vacías):
    # así fue entrenado, y el contexto de cada palabra es justamente lo que aprovecha.
    return [[float(x) for x in v] for v in modelo.encode(textos)]


def main():
    corpus = cargar_corpus()
    palabras = [preprocesar(a["abstract"]) for a in corpus]
    vocabulario = {p for lista in palabras for p in lista}

    print("Modelo 1: GloVe (50 dimensiones, promedio de las palabras)")
    glove = cargar_glove(vocabulario)
    salida_glove, cobertura = {}, []
    for articulo, lista in zip(corpus, palabras):
        vector, conocidas = promedio_glove(lista, glove)
        salida_glove[str(articulo["id"])] = vector
        cobertura.append((articulo["id"], conocidas, len(lista)))
        print(f"  artículo {articulo['id']:>2}: {conocidas} de {len(lista)} palabras con vector en GloVe")
    sin_vector = sorted(vocabulario - set(glove))
    print(f"  Palabras del corpus sin vector en GloVe: {len(sin_vector)} de {len(vocabulario)}"
          f" (ejemplos: {', '.join(sin_vector[:8])})")

    print(f"\nModelo 2: {NOMBRE_MINILM} (384 dimensiones, abstract completo)")
    minilm = vectores_minilm([a["abstract"] for a in corpus])
    salida_minilm = {str(a["id"]): v for a, v in zip(corpus, minilm)}
    print(f"  {len(salida_minilm)} vectores de {len(minilm[0])} dimensiones")

    resultado = {
        "glove": {"nombre": "GloVe wiki-gigaword (50 dimensiones)", "dimensiones": 50,
                  "vectores": salida_glove,
                  "cobertura": {str(i): [c, t] for i, c, t in cobertura},
                  "palabras_sin_vector": sin_vector},
        "minilm": {"nombre": NOMBRE_MINILM, "dimensiones": len(minilm[0]), "vectores": salida_minilm},
    }
    ruta = RESULTADOS / "req1_embeddings.json"
    ruta.write_text(json.dumps(resultado, ensure_ascii=False), encoding="utf-8")
    print(f"\nVectores guardados en resultados/{ruta.name}")


if __name__ == "__main__":
    main()
