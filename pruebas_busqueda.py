"""
Pruebas de los algoritmos de búsqueda (Requerimiento 3)
=======================================================
1. Casos pequeños resueltos a mano (se pueden verificar en papel).
2. Casos borde: patrón más largo que el texto, texto vacío, ocurrencias solapadas.
3. 20.000 textos y patrones aleatorios: KMP, Boyer-Moore y Rabin-Karp deben dar
   exactamente las mismas posiciones que la fuerza bruta. Rabin-Karp se prueba
   también con un primo pequeño (q = 13) para forzar muchas colisiones.

Uso: python pruebas_busqueda.py
"""

import random

import busqueda as b

ALGORITMOS = {
    "fuerza bruta": b.fuerza_bruta,
    "KMP": b.kmp,
    "Boyer-Moore": b.boyer_moore,
    "Rabin-Karp": b.rabin_karp,
    "Rabin-Karp (q = 13)": lambda t, p: b.rabin_karp(t, p, primo=13),
}

# (texto, patrón, posiciones esperadas) -> resueltos a mano
CASOS = [
    ("abracadabra", "abra", [0, 7]),
    ("aaaaa", "aa", [0, 1, 2, 3]),                 # ocurrencias solapadas
    ("abababab", "abab", [0, 2, 4]),
    ("neural fuzzy systems", "systems", [13]),
    ("systematic review", "systems", []),           # coincidencia parcial que no termina
    ("abc", "abcd", []),                            # patrón más largo que el texto
    ("", "a", []),                                  # texto vacío
    ("a", "a", [0]),
    ("generative ai and ai", "ai", [11, 18]),
]

# Tablas auxiliares calculadas a mano
TABLAS = [
    ("tabla_prefijos('abab')", b.tabla_prefijos("abab"), [0, 0, 1, 2]),
    ("tabla_prefijos('systems')", b.tabla_prefijos("systems"), [0, 0, 1, 0, 0, 0, 1]),
    ("tabla_caracter_malo('systems')", b.tabla_caracter_malo("systems"),
     {"s": 6, "y": 1, "t": 3, "e": 4, "m": 5}),
    ("tabla_sufijo_bueno('abcab')", b.tabla_sufijo_bueno("abcab"), [3, 3, 3, 3, 3, 1]),
    ("tabla_sufijo_bueno('systems')", b.tabla_sufijo_bueno("systems"), [6, 6, 6, 6, 6, 6, 4, 1]),
]


def main():
    fallos = 0
    for nombre, obtenido, esperado in TABLAS:
        if obtenido != esperado:
            fallos += 1
            print(f"FALLO {nombre}: {obtenido} != {esperado}")
    for texto, patron, esperado in CASOS:
        for nombre, algoritmo in ALGORITMOS.items():
            if algoritmo(texto, patron)[0] != esperado:
                fallos += 1
                print(f"FALLO {nombre}: '{patron}' en '{texto}'")
    print(f"Tablas y casos a mano: {len(TABLAS)} tablas y {len(CASOS)} casos x "
          f"{len(ALGORITMOS)} algoritmos")

    random.seed(2026)
    aleatorios = 20_000
    for _ in range(aleatorios):
        alfabeto = random.choice(["ab", "abc", "acgt", "abcdefghij"])
        texto = "".join(random.choice(alfabeto) for _ in range(random.randint(0, 80)))
        patron = "".join(random.choice(alfabeto) for _ in range(random.randint(1, 8)))
        referencia = b.fuerza_bruta(texto, patron)[0]
        for nombre, algoritmo in ALGORITMOS.items():
            if algoritmo(texto, patron)[0] != referencia:
                fallos += 1
                print(f"FALLO {nombre}: '{patron}' en '{texto}'")
    print(f"Casos aleatorios: {aleatorios:,} x {len(ALGORITMOS) - 1} algoritmos comparados con la fuerza bruta"
          .replace(",", "."))
    print("\nResultado:", "TODAS LAS PRUEBAS PASARON" if fallos == 0 else f"{fallos} FALLOS")


if __name__ == "__main__":
    main()
