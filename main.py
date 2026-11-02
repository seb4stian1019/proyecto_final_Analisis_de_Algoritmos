"""
Ejecuta todo el proyecto en orden.
Uso: python main.py
"""

import sys

import paso1_corpus
import pruebas_busqueda
import pruebas_similitud
import req1_caso_estudio
import req1_embeddings
import req1_similitud
import req3_busqueda
import req3_caso_estudio
import req3_tiempos
from datos import RESULTADOS


def main():
    print("=== Paso 1: título, autores y abstract de cada PDF ===")
    paso1_corpus.main()

    print("\n=== Requerimiento 1: pruebas de los algoritmos de similitud ===")
    pruebas_similitud.main()

    print("\n=== Requerimiento 1: vectores de los modelos de IA ===")
    if (RESULTADOS / "req1_embeddings.json").exists():
        print("Se usan los vectores ya guardados en resultados/req1_embeddings.json "
              "(para recalcularlos: python req1_embeddings.py)")
    else:
        req1_embeddings.main()

    print("\n=== Requerimiento 1: matrices de similitud de los 20 abstracts ===")
    sys.argv = ["req1_similitud.py"]
    req1_similitud.main()

    print("\n=== Requerimiento 1: caso de estudio paso a paso (artículos 11 y 16) ===")
    req1_caso_estudio.main()

    print("\n=== Requerimiento 3: pruebas de los algoritmos de búsqueda ===")
    pruebas_busqueda.main()

    print("\n=== Requerimiento 3: ejemplo de búsqueda en el corpus ===")
    sys.argv = ["req3_busqueda.py", "generative ai"]
    req3_busqueda.main()

    print("\n=== Requerimiento 3: caso de estudio paso a paso ===")
    req3_caso_estudio.main()

    print("\n=== Requerimiento 3: medición de tiempos ===")
    req3_tiempos.main()


if __name__ == "__main__":
    main()
