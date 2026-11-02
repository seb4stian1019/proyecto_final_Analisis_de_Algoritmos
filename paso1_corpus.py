"""
PASO 1 - Construir el corpus: título, autores y abstract de cada artículo
==========================================================================
Proyecto final 2026-2: Análisis de algoritmos en el contexto de la bibliometría

Entrada : carpeta con los 20 PDF entregados por el docente (por defecto ./articulos)
Salida  : resultados/corpus.json  ->  lista de {"id", "archivo", "titulo", "autores",
                                                "abstract", "palabras"}

La extracción del abstract es la misma del seguimiento (ya verificada).
Lo nuevo es la extracción del título y de los autores (sección B).

Instalación:  pip install pdfminer.six
Uso:          python paso1_corpus.py [carpeta_de_los_pdf]
"""

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LAParams, LTChar, LTTextContainer, LTTextLine

# Carpeta donde está este script: así las rutas funcionan sin importar desde dónde se ejecute.
BASE = Path(__file__).resolve().parent

# pdfminer reconstruye el orden de lectura agrupando el texto en bloques (columnas).
# line_margin=1.0 (por defecto 0.5) deja en un mismo bloque líneas con interlineado
# amplio; sin esto, el abstract del artículo de Wiley (14) sale partido línea por línea.
PARAMETROS = LAParams(line_margin=1.0)


# ===========================================================================
# A. ABSTRACT (igual que en el seguimiento)
# ===========================================================================
def espaciada(palabra):
    """'ABSTRACT' -> patrón que acepta 'ABSTRACT' y también 'A B S T R A C T'."""
    return r"\s*".join(palabra)


# Inicio: el encabezado del resumen. Cada editorial lo escribe distinto:
#   Elsevier "A B S T R A C T" | Springer/Emerald/Wiley "Abstract" | MDPI "Abstract:"
INICIO = re.compile(rf"^\s*(?:{espaciada('ABSTRACT')}|Abstract)\s*:?", re.MULTILINE)

# Encabezado de palabras clave: "Keywords", "KEYWORDS" o "K E Y W O R D S".
# Solo cuenta al inicio de una línea: la palabra "keywords" también puede
# aparecer dentro del texto del resumen (pasa en el artículo 15).
PALABRAS_CLAVE = rf"(?:{espaciada('KEYWORDS')}|Keywords)"

# Fin: lo primero que aparezca entre las palabras clave, el recuadro "Citation:"
# de MDPI, el título "Introduction" o una línea en blanco (fin del párrafo).
FIN = re.compile(
    rf"^\s*(?:{PALABRAS_CLAVE}|Citation:|(?:\d\.\s*)?Introduction\b)|\n\s*\n",
    re.MULTILINE,
)

# Rótulos del resumen estructurado de Emerald (artículo 13). Son parte de la
# plantilla de la revista, no texto de los autores, así que se eliminan.
ROTULOS = re.compile(
    r"^(?:Purpose|Design/methodology/approach|Findings|Research limitations/implications"
    r"|Practical implications|Social implications|Originality/value)\s*[–-]\s*",
    re.MULTILINE,
)

# Palabra partida con guion al final de una línea, por ejemplo "edu-⏎cation".
PARTIDA = re.compile(r"(\w+)-[ \t]*\n\s*(\w+)")


def normalizar(texto):
    """NFKC convierte ligaduras tipográficas ('ﬁ' -> 'fi', 'ﬀ' -> 'ff') y espacios
    especiales en caracteres normales. También quitamos el guion suave invisible."""
    return unicodedata.normalize("NFKC", texto).replace("­", "")


def recortar_abstract(texto):
    """Devuelve el texto que hay entre el encabezado del abstract y el primer marcador de fin."""
    inicio = INICIO.search(texto)
    if inicio is None:
        return None
    resto = texto[inicio.end():].lstrip()

    # Elsevier usa dos columnas: la izquierda (palabras clave) sale justo después
    # del encabezado. Si es así, saltamos ese bloque hasta la primera línea en blanco.
    if re.match(PALABRAS_CLAVE, resto):
        resto = resto[re.search(r"\n\s*\n", resto).end():].lstrip()

    fin = FIN.search(resto)
    return resto[: fin.start()] if fin else resto


def construir_lexico(ruta_pdf):
    """Conjunto (set) con todas las palabras del artículo completo.
    Un set es una tabla hash: preguntar si una palabra está cuesta O(1) en promedio."""
    texto = normalizar(extract_text(ruta_pdf, laparams=PARAMETROS)).lower()
    return set(re.findall(r"[a-z]+(?:-[a-z]+)*", texto))


def reparar_guiones(abstract, ruta_pdf):
    """Une las palabras que la maquetación partió al final de una línea.
    'education' debe quedar 'education', pero 'AI-⏎driven' debe quedar 'AI-driven'.
    Para decidir, miramos cómo aparece la palabra en el resto del mismo artículo."""
    if not PARTIDA.search(abstract):
        return abstract
    lexico = construir_lexico(ruta_pdf)

    def decidir(m):
        a, b = m.group(1), m.group(2)
        if (a + b).lower() in lexico:
            return a + b            # existe unida      -> era un corte de sílaba
        if f"{a}-{b}".lower() in lexico:
            return f"{a}-{b}"       # existe con guion  -> es una palabra compuesta
        return a + b                # sin evidencia: lo más frecuente es el corte de sílaba

    return PARTIDA.sub(decidir, abstract)


def limpiar(abstract):
    """Quita los rótulos de Emerald y deja todo en una sola línea con espacios simples."""
    abstract = ROTULOS.sub("", abstract)
    return re.sub(r"\s+", " ", abstract).strip()


def extraer_abstract(ruta_pdf):
    """Proceso completo para un artículo: el abstract siempre está en la página 1."""
    pagina1 = normalizar(extract_text(ruta_pdf, page_numbers=[0], laparams=PARAMETROS))
    abstract = recortar_abstract(pagina1)
    if abstract is None:
        return None
    abstract = reparar_guiones(abstract, ruta_pdf)
    return limpiar(abstract)


# ===========================================================================
# B. TÍTULO Y AUTORES (nuevo en el proyecto final)
# ===========================================================================
# Idea: en la primera página el título es el texto con la LETRA MÁS GRANDE,
# y los autores están en las líneas que vienen justo debajo del título.
#
# Única excepción: en los artículos de Elsevier (1 a 10) el nombre de la revista
# del encabezado tiene una letra un poco más grande que el título, así que esa
# línea se ignora.
ENCABEZADO_ELSEVIER = "Computers and Education"

# Los autores están como máximo a esta distancia (en puntos) debajo del título.
DISTANCIA_AUTORES = 70


def lineas_primera_pagina(ruta_pdf):
    """Devuelve las líneas de la página 1 con su tamaño de letra y su posición.
    pdfminer da cada carácter con su tamaño (c.size) y cada línea con su altura en
    la página (y1: más grande = más arriba)."""
    lineas = []
    for pagina in extract_pages(ruta_pdf, page_numbers=[0]):
        for bloque in pagina:
            if not isinstance(bloque, LTTextContainer):
                continue
            for linea in bloque:
                if not isinstance(linea, LTTextLine):
                    continue
                letras = [c for c in linea if isinstance(c, LTChar)]
                if not letras:
                    continue
                # Tamaño de la línea = el tamaño de letra que más se repite en ella.
                tamano = Counter(round(c.size, 1) for c in letras).most_common(1)[0][0]
                # Los superíndices de afiliación ("Chiu a,*", "Xia3") se escriben con
                # letra más pequeña: los cambiamos por un espacio para descartarlos.
                texto = "".join(
                    c.get_text() if not isinstance(c, LTChar) or c.size >= 0.85 * tamano else " "
                    for c in linea
                )
                lineas.append({"tamano": tamano, "y": linea.y1, "x": linea.x0,
                               "texto": normalizar(texto).strip()})
    return lineas


def en_orden_de_lectura(lineas):
    """Ordena de arriba hacia abajo y, en una misma altura, de izquierda a derecha.
    Se redondea y/4 para que trozos de una misma línea visual queden juntos."""
    return sorted(lineas, key=lambda l: (-round(l["y"] / 4), l["x"]))


def separar_autores(texto):
    """'Qi Xia , Xiaojing Weng and Thomas Chiu*' -> ['Qi Xia', 'Xiaojing Weng', 'Thomas Chiu']"""
    texto = texto.replace("*", " ").replace("∗", " ")
    # Acento suelto que algunos PDF ponen antes de la letra: "Gaševi ́c" -> "Gašević"
    texto = re.sub(r"\s*́(\w)", lambda m: unicodedata.normalize("NFC", m.group(1) + "́"), texto)
    # Separadores entre autores según la editorial: coma, "and", "|" (Wiley), "·" (Springer)
    partes = re.split(r",|\band\b|\||·", texto)
    return [re.sub(r"\s+", " ", p).strip() for p in partes if p.strip()]


def extraer_titulo_y_autores(ruta_pdf):
    lineas = [l for l in lineas_primera_pagina(ruta_pdf)
              if not l["texto"].startswith(ENCABEZADO_ELSEVIER)]

    # 1) Título: todas las líneas con el tamaño de letra máximo.
    tamano_titulo = max(l["tamano"] for l in lineas)
    lineas_titulo = en_orden_de_lectura([l for l in lineas if l["tamano"] == tamano_titulo])
    titulo = " ".join(l["texto"] for l in lineas_titulo).replace("\u2010", "-")  # guion tipográfico
    borde_inferior = min(l["y"] for l in lineas_titulo)

    # 2) Autores: líneas con letras que están justo debajo del título...
    debajo = [l for l in lineas
              if borde_inferior - DISTANCIA_AUTORES < l["y"] < borde_inferior
              and re.search(r"[A-Za-z]{2}", l["texto"])]
    if not debajo:
        return titulo, []
    # ...y que tienen el mismo tamaño de letra que la primera de ellas
    # (así no se mezclan las afiliaciones, que van con otra letra).
    primera = max(debajo, key=lambda l: l["y"])
    lineas_autores = en_orden_de_lectura(
        [l for l in debajo if abs(l["tamano"] - primera["tamano"]) < 0.3])
    autores = separar_autores(" ".join(l["texto"] for l in lineas_autores))
    return titulo, autores


# ===========================================================================
# Programa principal
# ===========================================================================
def numero_articulo(ruta):
    """Los archivos empiezan con su número ('7. Human-centred...pdf'); lo usamos como id."""
    m = re.match(r"\d+", ruta.name)
    return int(m.group()) if m else None


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "articulos"
    # rglob también encuentra los PDF que quedaron dentro de una subcarpeta al descomprimir.
    pdfs = sorted(carpeta.rglob("*.pdf"), key=lambda r: (numero_articulo(r) or 999, r.name))
    if not pdfs:
        # Se detiene antes de sobrescribir resultados/corpus.json con un corpus vacío.
        raise SystemExit(f"No hay archivos PDF en {carpeta}. Copie allí los 20 artículos "
                         "(descomprimidos, no dentro de un .zip).")

    corpus = []
    for i, ruta in enumerate(pdfs, start=1):
        abstract = extraer_abstract(ruta)
        if abstract is None:
            print(f"[AVISO] No se encontró el encabezado del abstract en: {ruta.name}")
            continue
        titulo, autores = extraer_titulo_y_autores(ruta)
        id_articulo = numero_articulo(ruta) or i
        corpus.append({
            "id": id_articulo,
            "archivo": ruta.name,
            "titulo": titulo,
            "autores": autores,
            "abstract": abstract,
            "palabras": len(abstract.split()),
        })
        # Líneas de verificación: compáralas con la primera página del PDF.
        print(f"{id_articulo:>2} | {titulo}")
        print(f"   | {'; '.join(autores)}  ({len(abstract.split())} palabras de abstract)")

    salida = BASE / "resultados" / "corpus.json"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    total_autores = sum(len(a["autores"]) for a in corpus)
    print(f"\n{len(corpus)} artículos guardados en resultados/corpus.json "
          f"({total_autores} autores en total)")


if __name__ == "__main__":
    main()
