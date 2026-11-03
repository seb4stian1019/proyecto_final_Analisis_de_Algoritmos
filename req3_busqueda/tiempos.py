"""
REQUERIMIENTO 3 - Medición de tiempos: preprocesamiento frente a búsqueda
=========================================================================
El enunciado pide contrastar la complejidad teórica (Big O) con el rendimiento
observado, separando el tiempo de PREPROCESAMIENTO (tablas o hash del patrón)
del tiempo de BÚSQUEDA (recorrido del texto).

Texto: los 20 abstracts unidos en uno solo, en minúsculas.
Experimento 1 - largo del patrón (m): prefijos de "artificial intelligence in education
               ..." de 2, 4, 8, 16, 32 y 64 caracteres (todos aparecen en el corpus).
Experimento 2 - largo del texto (n): el corpus repetido 1, 2, 4, 8 y 16 veces, con el
               patrón fijo "learning" (m = 8).

Se usa la misma metodología del seguimiento: reloj perf_counter_ns, calentamiento,
recolector de basura desactivado, orden aleatorio en cada ronda y la MEDIANA.

Salida: resultados/req3_tiempos_patron.csv, resultados/req3_tiempos_texto.csv,
        resultados/req3_grafico_patron.png, resultados/req3_grafico_texto.png,
        resultados/req3_entorno.txt
Requiere: pip install matplotlib
Uso: python -m req3_busqueda.tiempos
"""

import csv
import gc
import platform
import random
import statistics
import time
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from req3_busqueda import busqueda as b
from paso1_corpus.datos import RESULTADOS, cargar_corpus

# Cada algoritmo separado en (preprocesar, buscar). buscar recibe lo que devuelve preprocesar.
ALGORITMOS = {
    "KMP": (b.tabla_prefijos,
            lambda t, p, pre: b.kmp_buscar(t, p, pre)),
    "Boyer-Moore": (lambda p: (b.tabla_caracter_malo(p), b.tabla_sufijo_bueno(p)),
                    lambda t, p, pre: b.boyer_moore_buscar(t, p, *pre)),
    "Rabin-Karp": (b.rabin_karp_preprocesar,
                   lambda t, p, pre: b.rabin_karp_buscar(t, p, *pre)),
}
COLORES = {"KMP": "#2E5597", "Boyer-Moore": "#C55A11", "Rabin-Karp": "#548235"}

LARGOS_PATRON = [2, 4, 8, 16, 32, 64]
FRASE = "artificial intelligence"           # se toman los caracteres desde su primera aparición
REPETICIONES_TEXTO = [1, 2, 4, 8, 16]
PATRON_FIJO = "learning"
RONDAS = 50                                 # mediciones por algoritmo y caso
CALENTAMIENTO = 3
SEMILLA = 2026


def ms(inicio, fin):
    return (fin - inicio) / 1_000_000


def medir_caso(texto, patron):
    """Devuelve {algoritmo: (mediana_preprocesamiento_ms, mediana_busqueda_ms, ocurrencias)}."""
    nombres = list(ALGORITMOS)
    for nombre in nombres:                  # calentamiento: no se mide
        pre_f, bus_f = ALGORITMOS[nombre]
        for _ in range(CALENTAMIENTO):
            bus_f(texto, patron, pre_f(patron))
    pre = {n: [] for n in nombres}
    bus = {n: [] for n in nombres}
    ocurrencias = {}
    gc.collect()
    gc.disable()
    try:
        for _ in range(RONDAS):
            random.shuffle(nombres)
            for nombre in nombres:
                pre_f, bus_f = ALGORITMOS[nombre]
                t0 = time.perf_counter_ns()
                tablas = pre_f(patron)
                t1 = time.perf_counter_ns()
                resultado = bus_f(texto, patron, tablas)
                t2 = time.perf_counter_ns()
                pre[nombre].append(ms(t0, t1))
                bus[nombre].append(ms(t1, t2))
                ocurrencias[nombre] = len(resultado[0])
    finally:
        gc.enable()
    return {n: (statistics.median(pre[n]), statistics.median(bus[n]), ocurrencias[n]) for n in ALGORITMOS}


def ajuste_lineal(xs, ys):
    """Recta de mínimos cuadrados y = a·x + b y su R² (qué tan recta es la relación).
    R² cercano a 1 confirma que el tiempo crece en forma lineal con n."""
    k = len(xs)
    mx, my = sum(xs) / k, sum(ys) / k
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    a = sxy / sxx
    b0 = my - a * mx
    ss_res = sum((y - (a * x + b0)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return a, b0, 1 - ss_res / ss_tot


def comparaciones(texto, patron):
    return {n: ALGORITMOS[n][1](texto, patron, ALGORITMOS[n][0](patron))[1] for n in ALGORITMOS}


def guardar_csv(nombre, encabezado, filas):
    with open(RESULTADOS / nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)


def miles(x):
    """28199 -> '28.199' (formato colombiano)."""
    return f"{x:,}".replace(",", ".")


DECIMAL = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def grafico(filas, x_col, x_nombre, titulo, archivo, logx=False, solo_busqueda=False):
    """Tiempo de preprocesamiento y de búsqueda (o solo búsqueda) en función de x."""
    paneles = [("bus", "Búsqueda (ms)")] if solo_busqueda else [("pre", "Preprocesamiento (ms)"),
                                                                ("bus", "Búsqueda (ms)")]
    fig, ejes = plt.subplots(1, len(paneles), figsize=(5.5 * len(paneles), 4), dpi=150, squeeze=False)
    for eje, (col, subtitulo) in zip(ejes[0], paneles):
        for nombre in ALGORITMOS:
            datos = [f for f in filas if f["algoritmo"] == nombre]
            eje.plot([f[x_col] for f in datos], [f[col] for f in datos], marker="o",
                     color=COLORES[nombre], label=nombre)
        eje.set_title(subtitulo, fontsize=10)
        eje.set_xlabel(x_nombre)
        eje.grid(alpha=0.3)
        eje.yaxis.set_major_formatter(DECIMAL)
        if logx:
            eje.set_xscale("log", base=2)
            eje.set_xticks(sorted({f[x_col] for f in filas}))
        eje.xaxis.set_major_formatter(FuncFormatter(lambda v, _: miles(int(v))))
    ejes[0][-1].legend(frameon=False)
    fig.suptitle(titulo, fontsize=11)
    fig.tight_layout()
    fig.savefig(RESULTADOS / archivo)
    plt.close(fig)


def main():
    random.seed(SEMILLA)
    texto = " ".join(a["abstract"] for a in cargar_corpus()).lower()
    n = len(texto)

    # ---- Experimento 1: varía m ----
    inicio = b.kmp(texto, FRASE)[0][0]
    filas1 = []
    print(f"Experimento 1: texto de n = {miles(n)} caracteres, patrón de m caracteres")
    print(f"{'m':>3}  {'patrón':<36}{'algoritmo':<13}{'prep. (ms)':>11}{'búsq. (ms)':>11}{'comparac.':>11}")
    for m in LARGOS_PATRON:
        patron = texto[inicio:inicio + m]
        resultado = medir_caso(texto, patron)
        comp = comparaciones(texto, patron)
        for nombre, (pre, bus, oc) in resultado.items():
            filas1.append({"m": m, "patron": patron, "algoritmo": nombre, "pre": pre, "bus": bus,
                           "comparaciones": comp[nombre], "ocurrencias": oc})
            print(f"{m:>3}  {patron[:34]:<36}{nombre:<13}{pre:>11.4f}{bus:>11.4f}{comp[nombre]:>11}")
    guardar_csv("req3_tiempos_patron.csv",
                ["m", "patron", "algoritmo", "preprocesamiento_ms", "busqueda_ms", "comparaciones", "ocurrencias"],
                [[f["m"], f["patron"], f["algoritmo"], f"{f['pre']:.5f}", f"{f['bus']:.5f}",
                  f["comparaciones"], f["ocurrencias"]] for f in filas1])
    grafico(filas1, "m", "Largo del patrón m (caracteres)",
            f"Tiempo según el largo del patrón (n = {miles(n)} caracteres)",
            "req3_grafico_patron.png", logx=True)

    # ---- Experimento 2: varía n ----
    filas2 = []
    print(f"\nExperimento 2: patrón fijo \"{PATRON_FIJO}\" (m = {len(PATRON_FIJO)}), texto de n caracteres")
    for veces in REPETICIONES_TEXTO:
        texto_n = " ".join([texto] * veces)
        resultado = medir_caso(texto_n, PATRON_FIJO)
        comp = comparaciones(texto_n, PATRON_FIJO)
        for nombre, (pre, bus, oc) in resultado.items():
            filas2.append({"n": len(texto_n), "algoritmo": nombre, "pre": pre, "bus": bus,
                           "comparaciones": comp[nombre], "ocurrencias": oc})
            print(f"{len(texto_n):>8}  {nombre:<13}{pre:>11.4f}{bus:>11.4f}{comp[nombre]:>11}")
    guardar_csv("req3_tiempos_texto.csv",
                ["n", "algoritmo", "preprocesamiento_ms", "busqueda_ms", "comparaciones", "ocurrencias"],
                [[f["n"], f["algoritmo"], f"{f['pre']:.5f}", f"{f['bus']:.5f}", f["comparaciones"],
                  f["ocurrencias"]] for f in filas2])
    ajustes = []
    print("\nAjuste lineal del tiempo de búsqueda frente a n:")
    for nombre in ALGORITMOS:
        datos = [f for f in filas2 if f["algoritmo"] == nombre]
        a, b0, r2 = ajuste_lineal([f["n"] for f in datos], [f["bus"] for f in datos])
        ajustes.append([nombre, f"{a * 1000:.5f}", f"{r2:.5f}"])
        print(f"  {nombre:<12} {a * 1000:.4f} µs por carácter   R² = {r2:.4f}")
    guardar_csv("req3_ajuste_lineal.csv", ["algoritmo", "microsegundos_por_caracter", "r2"], ajustes)
    grafico(filas2, "n", "Largo del texto n (caracteres)",
            f"Tiempo según el largo del texto (patrón \"{PATRON_FIJO}\")", "req3_grafico_texto.png", solo_busqueda=True)

    (RESULTADOS / "req3_entorno.txt").write_text(
        f"Fecha: {datetime.now():%Y-%m-%d %H:%M}\n"
        f"Sistema: {platform.platform()}\n"
        f"Procesador: {platform.processor() or platform.machine()}\n"
        f"Python: {platform.python_version()}\n", encoding="utf-8")
    print("\nTablas y gráficos guardados en resultados/")


if __name__ == "__main__":
    main()
