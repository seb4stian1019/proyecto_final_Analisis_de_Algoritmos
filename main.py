"""
Ejecuta todo el proyecto en orden: Paso 1, Requerimiento 1, 2 y 3.
Uso (en la raíz del proyecto):  python main.py
"""

import sys

import paso1_corpus.extraer
import paso1_corpus.verificar
import req1_similitud.caso_estudio
import req1_similitud.comparar
import req1_similitud.embeddings
import req1_similitud.pruebas
import req2_agrupamiento.caso_estudio
import req2_agrupamiento.dendrogramas
import req2_agrupamiento.pruebas
import req3_busqueda.buscar_patron
import req3_busqueda.caso_estudio
import req3_busqueda.pruebas
import req3_busqueda.tiempos
from paso1_corpus.datos import RESULTADOS


def main():
    print("=== Paso 1: título, autores y abstract de cada PDF ===")
    paso1_corpus.extraer.main()

    print("\n=== Paso 1: verificación del corpus contra los PDF ===")
    paso1_corpus.verificar.main()

    print("\n=== Requerimiento 1: pruebas de los algoritmos de similitud ===")
    req1_similitud.pruebas.main()

    print("\n=== Requerimiento 1: vectores de los modelos de IA ===")
    if (RESULTADOS / "req1_embeddings.json").exists():
        print("Se usan los vectores ya guardados en resultados/req1_embeddings.json "
              "(para recalcularlos: python -m req1_similitud.embeddings)")
    else:
        req1_similitud.embeddings.main()

    print("\n=== Requerimiento 1: matrices de similitud de los 20 abstracts ===")
    sys.argv = ["comparar"]                      # sin argumentos: matrices 20 x 20
    req1_similitud.comparar.main()

    print("\n=== Requerimiento 1: caso de estudio paso a paso (artículos 11 y 16) ===")
    req1_similitud.caso_estudio.main()

    print("\n=== Requerimiento 2: pruebas del agrupamiento jerárquico ===")
    req2_agrupamiento.pruebas.main()

    print("\n=== Requerimiento 2: agrupamiento de los 20 abstracts y dendrogramas ===")
    req2_agrupamiento.dendrogramas.main()

    print("\n=== Requerimiento 2: caso de estudio paso a paso (artículos 2, 6, 11, 16 y 19) ===")
    req2_agrupamiento.caso_estudio.main()

    print("\n=== Requerimiento 3: pruebas de los algoritmos de búsqueda ===")
    req3_busqueda.pruebas.main()

    print("\n=== Requerimiento 3: ejemplo de búsqueda en el corpus ===")
    sys.argv = ["buscar_patron", "generative ai"]
    req3_busqueda.buscar_patron.main()

    print("\n=== Requerimiento 3: caso de estudio paso a paso ===")
    req3_busqueda.caso_estudio.main()

    print("\n=== Requerimiento 3: medición de tiempos ===")
    req3_busqueda.tiempos.main()


if __name__ == "__main__":
    main()
