"""
Lectura del corpus que genera el paso 1 (resultados/corpus.json).
Todos los requerimientos parten de aquí.
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "resultados"


def cargar_corpus():
    """Lista de artículos: {"id", "archivo", "titulo", "autores", "abstract", "palabras"}."""
    ruta = RESULTADOS / "corpus.json"
    if not ruta.exists():
        raise SystemExit("Falta resultados/corpus.json: ejecute primero  python paso1_corpus.py")
    return json.loads(ruta.read_text(encoding="utf-8"))
