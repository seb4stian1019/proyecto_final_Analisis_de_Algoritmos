"""
Verificación automática del corpus (evidencia del paso 1)
=========================================================
Comprueba que lo que extraer.py extrajo de cada PDF está de verdad en el PDF.

Para cada artículo se lee de nuevo el texto de la página 1 y se buscan en él:
  - el título completo,
  - cada uno de los autores,
  - cada oración del abstract.
La búsqueda usa nuestro KMP (req3_busqueda/busqueda.py).

Para comparar, los dos textos se "normalizan": se dejan solo las letras, en
minúsculas y sin espacios. Así no importan los saltos de línea, los guiones de
corte de palabra ("edu-⏎cation") ni los espacios dobles del PDF.

Salida: resultados/corpus_verificacion.csv (una fila por artículo)
Uso:    python -m paso1_corpus.verificar
"""

import csv
import unicodedata

from pdfminer.high_level import extract_text

from req3_busqueda.busqueda import kmp
from paso1_corpus.datos import	 BASE, RESULTADOS, cargar_corpus
from paso1_corpus.extraer import PARAMETROS


def normalizar(texto):
    """'Gašević, D.' -> 'gasevicd'  (solo letras a-z, sin tildes ni espacios)."""
    sin_tildes = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sin_tildes.lower() if "a" <= c <= "z")


def oraciones(texto):
    """Divide el abstract en oraciones: corta después de '. ' (recorrido carácter a carácter)."""
    partes, inicio = [], 0
    for k in range(len(texto) - 1):
        if texto[k] == "." and texto[k + 1] == " ":
            partes.append(texto[inicio:k + 1])
            inicio = k + 2
    partes.append(texto[inicio:])
    return [p for p in partes if len(normalizar(p)) >= 10]   # descarta trozos como "e.g."


def esta(fragmento, pagina):
    return len(kmp(pagina, normalizar(fragmento))[0]) > 0


def main():
    filas = []
    for articulo in cargar_corpus():
        pagina = normalizar(extract_text(BASE / "articulos" / articulo["archivo"],
                                         page_numbers=[0], laparams=PARAMETROS))
        lista = oraciones(articulo["abstract"])
        encontradas = sum(1 for o in lista if esta(o, pagina))
        autores = sum(1 for a in articulo["autores"] if esta(a, pagina))
        fila = {
            "id": articulo["id"],
            "titulo_encontrado": "sí" if esta(articulo["titulo"], pagina) else "NO",
            "autores_encontrados": f"{autores}/{len(articulo['autores'])}",
            "oraciones_abstract_encontradas": f"{encontradas}/{len(lista)}",
        }
        filas.append(fila)
        print(f"{fila['id']:>2}  título: {fila['titulo_encontrado']:<3} autores: {fila['autores_encontrados']:<6}"
              f"oraciones del abstract: {fila['oraciones_abstract_encontradas']}")

    with open(RESULTADOS / "corpus_verificacion.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print("\nResultado guardado en resultados/corpus_verificacion.csv")


if __name__ == "__main__":
    main()
