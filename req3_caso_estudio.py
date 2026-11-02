"""
REQUERIMIENTO 3 - Caso de estudio paso a paso
==============================================
El enunciado pide seleccionar un patrón y un párrafo de uno de los abstracts y
mostrar, paso a paso, cómo se llenan las estructuras auxiliares de cada algoritmo
y cómo se desplaza el patrón sobre el texto.

Caso elegido:
  Patrón  : "systems"  (m = 7). Tiene letras repetidas ('s' tres veces), así que
            las tablas de KMP y de Boyer-Moore no quedan triviales.
  Párrafo : una oración del abstract del artículo 17. Contiene la palabra
            "systematic", que empieza igual que el patrón ("system...") y obliga
            a los algoritmos a resolver una coincidencia parcial.

Este script repite los algoritmos de busqueda.py, pero guardando cada paso
(traza). Al final comprueba que la traza dé el mismo resultado que busqueda.py.

Salida: resultados/req3_caso_estudio.json  (lo usa el documento)
Uso:    python req3_caso_estudio.py
"""

import json

import busqueda as b
from datos import RESULTADOS, cargar_corpus

PATRON = "systems"
ARTICULO = 17
INICIO_ORACION = "Moreover, the systematic review"
FIN_ORACION = "educational assessment."
PRIMO_PEQUENO = 101         # q pequeño (valor típico de los ejemplos) para que se vean colisiones


def obtener_parrafo():
    """Toma del abstract del artículo 17 la oración que empieza con INICIO_ORACION.
    La ubicamos con nuestra propia búsqueda (KMP), no con find()."""
    articulo = next(a for a in cargar_corpus() if a["id"] == ARTICULO)
    abstract = articulo["abstract"]
    inicio = b.kmp(abstract, INICIO_ORACION)[0][0]
    # la oración tiene "e.g." por dentro, así que el final se busca por su texto
    fin = [f for f in b.kmp(abstract, FIN_ORACION)[0] if f > inicio][0] + len(FIN_ORACION)
    return articulo, abstract[inicio:fin].lower()


# ---------------------------------------------------------------------------
# KMP
# ---------------------------------------------------------------------------
def traza_tabla_prefijos(p):
    m, pi, k, pasos = len(p), [0] * len(p), 0, []
    for q in range(1, m):
        k_antes, retrocesos = k, []
        while k > 0 and p[k] != p[q]:
            retrocesos.append(k)
            k = pi[k - 1]
        coincide = p[k] == p[q]
        if coincide:
            k += 1
        pi[q] = k
        pasos.append({"q": q, "caracter": p[q], "k_antes": k_antes, "retrocesos": retrocesos,
                      "compara_con": p[k - 1] if coincide else p[k], "coincide": coincide, "pi": k})
    return pi, pasos


def traza_kmp(t, p, pi):
    """Guarda solo los pasos con algo que contar: avances del patrón, fallos con
    retroceso por la tabla y ocurrencias. Los fallos con q = 0 se resumen."""
    m, q, eventos, posiciones = len(p), 0, [], []
    saltados = 0
    for i, c in enumerate(t):
        q_antes, retrocesos = q, []
        while q > 0 and p[q] != c:
            retrocesos.append(q)
            q = pi[q - 1]
        if p[q] == c:
            q += 1
        encontrado = q == m
        if q_antes == 0 and q == 0:
            saltados += 1                                # fallo directo contra p[0]
            continue
        if saltados:
            eventos.append({"tipo": "salto", "cantidad": saltados})
            saltados = 0
        eventos.append({"i": i, "caracter": c, "q_antes": q_antes, "retrocesos": retrocesos,
                        "q_despues": q, "encontrado": encontrado})
        if encontrado:
            posiciones.append(i - m + 1)
            q = pi[q - 1]
    if saltados:
        eventos.append({"tipo": "salto", "cantidad": saltados})
    return posiciones, eventos


# ---------------------------------------------------------------------------
# Boyer-Moore
# ---------------------------------------------------------------------------
def traza_boyer_moore(t, p, ultima, sufijo):
    n, m, s, filas, posiciones = len(t), len(p), 0, [], []
    while s <= n - m:
        j, comparados = m - 1, 0
        while j >= 0:
            comparados += 1
            if p[j] != t[s + j]:
                break
            j -= 1
        fila = {"s": s, "ventana": t[s:s + m], "comparaciones": comparados}
        if j < 0:
            posiciones.append(s)
            fila.update({"j": -1, "malo": None, "salto_malo": None, "salto_bueno": sufijo[0],
                         "salto": sufijo[0], "resultado": "ocurrencia"})
            s += sufijo[0]
        else:
            malo = t[s + j]
            salto_malo = j - ultima.get(malo, -1)
            salto_bueno = sufijo[j + 1]
            salto = max(salto_malo, salto_bueno, 1)
            fila.update({"j": j, "malo": malo, "salto_malo": salto_malo, "salto_bueno": salto_bueno,
                         "salto": salto, "resultado": "fallo"})
            s += salto
        filas.append(fila)
    return posiciones, filas


def explicar_sufijo_bueno(p, sufijo):
    """Para cada posición de fallo j: el sufijo bueno y el desplazamiento elegido."""
    m = len(p)
    return [{"j": j, "sufijo_bueno": p[j + 1:] if j < m - 1 else "", "desplazamiento": sufijo[j + 1]}
            for j in range(m - 1, -2, -1)]


# ---------------------------------------------------------------------------
# Rabin-Karp
# ---------------------------------------------------------------------------
def traza_rabin_karp(t, p, base, primo):
    m, n = len(p), len(t)
    pasos_patron, hp = [], 0
    for c in p:                                          # Horner sobre el patrón
        nuevo = (base * hp + ord(c)) % primo
        pasos_patron.append({"caracter": c, "codigo": ord(c), "hash_antes": hp, "hash": nuevo})
        hp = nuevo
    h = 1
    for _ in range(m - 1):
        h = (h * base) % primo
    hv = 0
    for i in range(m):
        hv = (base * hv + ord(t[i])) % primo
    ventanas, posiciones, colisiones = [], [], 0
    for s in range(n - m + 1):
        fila = {"s": s, "ventana": t[s:s + m], "hash": hv, "coincide_hash": hv == hp}
        if hv == hp:
            igual = True
            for j in range(m):
                if t[s + j] != p[j]:
                    igual = False
                    break
            fila["verificacion"] = "ocurrencia" if igual else "colisión"
            if igual:
                posiciones.append(s)
            else:
                colisiones += 1
        if s < n - m:
            fila["sale"], fila["entra"] = t[s], t[s + m]
            hv = (base * (hv - ord(t[s]) * h) + ord(t[s + m])) % primo
        ventanas.append(fila)
    return {"pasos_patron": pasos_patron, "hash_patron": hp, "h": h, "ventanas": ventanas,
            "posiciones": posiciones, "colisiones": colisiones}


def main():
    articulo, texto = obtener_parrafo()
    p = PATRON
    print(f'Artículo {articulo["id"]}: {articulo["titulo"]}')
    print(f'Párrafo (n = {len(texto)}): "{texto}"')
    print(f'Patrón (m = {len(p)}): "{p}"\n')

    # KMP
    pi, pasos_pi = traza_tabla_prefijos(p)
    pos_kmp, eventos_kmp = traza_kmp(texto, p, pi)
    print("KMP  tabla de prefijos pi =", pi, "  ocurrencias:", pos_kmp)

    # Boyer-Moore
    ultima = b.tabla_caracter_malo(p)
    sufijo = b.tabla_sufijo_bueno(p)
    pos_bm, filas_bm = traza_boyer_moore(texto, p, ultima, sufijo)
    print("BM   carácter malo =", ultima, "  sufijo bueno =", sufijo)
    print(f"     {len(filas_bm)} alineaciones del patrón, {sum(f['comparaciones'] for f in filas_bm)}"
          f" comparaciones, ocurrencias: {pos_bm}")

    # Rabin-Karp con primo pequeño y con primo grande
    rk = traza_rabin_karp(texto, p, b.BASE, PRIMO_PEQUENO)
    rk_grande = traza_rabin_karp(texto, p, b.BASE, b.PRIMO)
    print(f"RK   q = {PRIMO_PEQUENO}: hash del patrón = {rk['hash_patron']}, h = {rk['h']}, "
          f"{rk['colisiones']} colisiones, ocurrencias: {rk['posiciones']}")
    print(f"     q = {b.PRIMO}: {rk_grande['colisiones']} colisiones")

    # Verificación: las trazas deben dar lo mismo que busqueda.py y que la fuerza bruta
    referencia = b.fuerza_bruta(texto, p)[0]
    assert pi == b.tabla_prefijos(p)
    assert pos_kmp == b.kmp(texto, p)[0] == referencia
    assert pos_bm == b.boyer_moore(texto, p)[0] == referencia
    assert rk["posiciones"] == rk_grande["posiciones"] == referencia
    print("\nVerificación: las trazas coinciden con busqueda.py y con la fuerza bruta.")

    caso = {
        "articulo": {"id": articulo["id"], "titulo": articulo["titulo"]},
        "patron": p, "parrafo": texto, "ocurrencias": referencia,
        "comparaciones_fuerza_bruta": b.fuerza_bruta(texto, p)[1],
        "kmp": {"pi": pi, "pasos_pi": pasos_pi, "eventos": eventos_kmp,
                "comparaciones": b.kmp(texto, p)[1]},
        "boyer_moore": {"ultima": ultima, "sufijo": sufijo,
                        "sufijo_explicado": explicar_sufijo_bueno(p, sufijo), "filas": filas_bm,
                        "comparaciones": b.boyer_moore(texto, p)[1]},
        "rabin_karp": {"base": b.BASE, "primo_pequeno": PRIMO_PEQUENO, "primo_grande": b.PRIMO,
                       "pequeno": rk, "colisiones_primo_grande": rk_grande["colisiones"],
                       "hash_patron_grande": rk_grande["hash_patron"]},
    }
    (RESULTADOS / "req3_caso_estudio.json").write_text(
        json.dumps(caso, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Traza guardada en resultados/req3_caso_estudio.json")


if __name__ == "__main__":
    main()
