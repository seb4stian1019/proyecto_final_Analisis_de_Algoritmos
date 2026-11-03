# Paso 1: construcción del corpus

Antes de los requerimientos se extraen el título, los autores y el abstract de los 20 PDF de `articulos/`. Todos los requerimientos parten de `resultados/corpus.json`.

## Archivos, en orden de lectura

| Orden | Archivo | Qué hace |
|---|---|---|
| 1 | `extraer.py` | Lee cada PDF y extrae título, autores y abstract → `resultados/corpus.json` |
| 2 | `datos.py` | Lee `resultados/corpus.json`; lo usan todos los requerimientos |
| 3 | `verificar.py` | Busca en la página 1 de cada PDF el título, los autores y cada oración del abstract extraídos (con el KMP de `req3_busqueda/busqueda.py`) → `resultados/corpus_verificacion.csv` |

## Cómo ejecutarlo

Desde la raíz del proyecto (no desde esta carpeta):

```
python -m paso1_corpus.extraer
python -m paso1_corpus.verificar
```
