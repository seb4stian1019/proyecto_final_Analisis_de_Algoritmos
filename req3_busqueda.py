"""
REQUERIMIENTO 3 - Búsqueda de un patrón en los 20 abstracts
============================================================
El usuario escribe un patrón y el programa lo busca en el abstract de cada artículo
con los tres algoritmos (KMP, Boyer-Moore y Rabin-Karp). Además verifica que los
tres encuentren exactamente las mismas posiciones que la fuerza bruta.

La búsqueda no distingue mayúsculas de minúsculas: texto y patrón se pasan a
minúsculas antes de buscar.

Uso:  python req3_busqueda.py "generative ai"
      python req3_busqueda.py            (pregunta el patrón)
"""

import sys

from busqueda import boyer_moore, fuerza_bruta, kmp, rabin_karp
from datos import cargar_corpus

ALGORITMOS = {"KMP": kmp, "Boyer-Moore": boyer_moore, "Rabin-Karp": rabin_karp}


def buscar_en_corpus(patron, corpus):
    """Devuelve una fila por artículo con las ocurrencias y las comparaciones de cada algoritmo."""
    patron = patron.lower()
    filas = []
    for articulo in corpus:
        texto = articulo["abstract"].lower()
        referencia, _ = fuerza_bruta(texto, patron)
        fila = {"id": articulo["id"], "titulo": articulo["titulo"], "posiciones": referencia}
        for nombre, algoritmo in ALGORITMOS.items():
            posiciones, comparaciones = algoritmo(texto, patron)
            if posiciones != referencia:
                raise AssertionError(f"{nombre} no coincide con la fuerza bruta en el artículo {articulo['id']}")
            fila[nombre] = comparaciones
        filas.append(fila)
    return filas


def contexto(texto, posicion, largo, margen=35):
    """Fragmento del abstract alrededor de una ocurrencia, para mostrarla."""
    inicio = max(0, posicion - margen)
    fin = min(len(texto), posicion + largo + margen)
    return ("..." if inicio > 0 else "") + texto[inicio:fin] + ("..." if fin < len(texto) else "")


def main():
    patron = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Patrón a buscar: ")
    if not patron.strip():
        raise SystemExit("El patrón no puede estar vacío.")
    corpus = cargar_corpus()
    filas = buscar_en_corpus(patron, corpus)

    total = sum(len(f["posiciones"]) for f in filas)
    print(f'\nPatrón: "{patron}"  ->  {total} ocurrencias en '
          f'{sum(1 for f in filas if f["posiciones"])} de {len(filas)} artículos\n')
    for f, articulo in zip(filas, corpus):
        if f["posiciones"]:
            print(f'[{f["id"]:>2}] {f["titulo"]}')
            print(f'     posiciones: {f["posiciones"]}')
            print(f'     "{contexto(articulo["abstract"], f["posiciones"][0], len(patron))}"')

    print("\nComparaciones de caracteres en todo el corpus (menos es mejor):")
    for nombre in ALGORITMOS:
        print(f"  {nombre:<12} {sum(f[nombre] for f in filas):>8,}".replace(",", "."))
    print("  (Rabin-Karp solo compara caracteres cuando el hash coincide; su trabajo principal\n"
          "   es actualizar el hash de cada ventana del texto)")
    print("\nLos tres algoritmos encontraron las mismas posiciones que la fuerza bruta.")


if __name__ == "__main__":
    main()
