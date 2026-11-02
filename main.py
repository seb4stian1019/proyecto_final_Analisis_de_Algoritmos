"""
Ejecuta todo el proyecto en orden.
Uso: python main.py
"""

import sys

import paso1_corpus
import pruebas_busqueda
import req3_busqueda
import req3_caso_estudio
import req3_tiempos


def main():
    print("=== Paso 1: título, autores y abstract de cada PDF ===")
    paso1_corpus.main()

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
