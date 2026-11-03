"""
Algoritmos de búsqueda de patrones (coincidencia exacta de cadenas)
====================================================================
Requerimiento 3 del proyecto final.

Todos están programados a mano: solo se usan ciclos, listas, diccionarios y la
comparación de dos caracteres (==). No se usa find(), index(), "in" sobre cadenas
ni expresiones regulares.

Cada algoritmo tiene dos partes, para poder medirlas por separado:
  1. Preprocesamiento: se hace una sola vez con el patrón (tablas auxiliares).
  2. Búsqueda: recorre el texto usando esas tablas.

Todas las funciones de búsqueda devuelven (posiciones, comparaciones):
  posiciones   -> lista con el índice (desde 0) donde empieza cada ocurrencia
  comparaciones -> cuántas veces se comparó un carácter del texto con uno del patrón
                   (sirve para contrastar el análisis teórico con lo observado)
"""


# ===========================================================================
# 0. Fuerza bruta (referencia)
# ===========================================================================
def fuerza_bruta(texto, patron):
    """Prueba el patrón en cada posición del texto, de izquierda a derecha.
    Es la búsqueda lineal del núcleo 4 aplicada a cadenas. Peor caso O(n·m).
    Se usa como referencia para verificar los otros tres algoritmos."""
    n, m = len(texto), len(patron)
    posiciones, comparaciones = [], 0
    for s in range(n - m + 1):              # s = desplazamiento del patrón sobre el texto
        j = 0
        while j < m:
            comparaciones += 1
            if texto[s + j] != patron[j]:
                break
            j += 1
        if j == m:                          # coincidieron los m caracteres
            posiciones.append(s)
    return posiciones, comparaciones


# ===========================================================================
# 1. Knuth-Morris-Pratt (KMP)
# ===========================================================================
def tabla_prefijos(patron):
    """Tabla de fallos de KMP (también llamada función prefijo π).
    pi[q] = longitud del prefijo más largo del patrón que también es sufijo
            de patron[0..q], sin contar la cadena completa.
    Ejemplo: 'abab' -> [0, 0, 1, 2]
    Costo: O(m), porque k sube como máximo m veces en total y cada retroceso lo baja."""
    m = len(patron)
    pi = [0] * m
    k = 0                                   # longitud del prefijo que coincide hasta ahora
    for q in range(1, m):
        while k > 0 and patron[k] != patron[q]:
            k = pi[k - 1]                   # retrocede al siguiente prefijo-sufijo más corto
        if patron[k] == patron[q]:
            k += 1
        pi[q] = k
    return pi


def kmp_buscar(texto, patron, pi):
    """Recorre el texto UNA sola vez, sin retroceder nunca en el texto.
    Cuando hay un fallo, la tabla pi dice cuántos caracteres del patrón ya
    coinciden y se puede seguir desde ahí. Costo: O(n)."""
    n, m = len(texto), len(patron)
    posiciones, comparaciones = [], 0
    q = 0                                   # cuántos caracteres del patrón coinciden ya
    for i in range(n):
        while q > 0 and patron[q] != texto[i]:
            comparaciones += 1              # comparación que falló
            q = pi[q - 1]                   # se usa la tabla en vez de retroceder en el texto
        comparaciones += 1
        if patron[q] == texto[i]:
            q += 1
        if q == m:                          # ocurrencia completa
            posiciones.append(i - m + 1)
            q = pi[q - 1]                   # se sigue buscando (permite ocurrencias solapadas)
    return posiciones, comparaciones


def kmp(texto, patron):
    return kmp_buscar(texto, patron, tabla_prefijos(patron))


# ===========================================================================
# 2. Boyer-Moore (regla del carácter malo + regla del sufijo bueno)
# ===========================================================================
def tabla_caracter_malo(patron):
    """ultima[c] = última posición donde aparece el carácter c en el patrón.
    Si c no aparece, se toma -1 (el patrón puede saltar por completo ese carácter).
    Costo: O(m)."""
    ultima = {}
    for j in range(len(patron)):
        ultima[patron[j]] = j               # al recorrer de izquierda a derecha queda la última
    return ultima


def tabla_sufijo_bueno(patron):
    """sufijo[j + 1] = desplazamiento cuando el fallo ocurre en la posición j del patrón
    (los caracteres j+1 .. m-1 ya coincidieron: ese es el 'sufijo bueno').
    sufijo[0] es el desplazamiento después de encontrar el patrón completo.

    Se calcula directamente con la definición: se prueban los desplazamientos
    k = 1, 2, 3, ... y se elige el primero en el que el sufijo bueno vuelve a encajar
    con el patrón (las posiciones que quedan por fuera a la izquierda no se comparan).
    Costo: O(m³) en el peor caso; con patrones cortos (m ≤ 30) es despreciable."""
    m = len(patron)
    sufijo = [0] * (m + 1)
    for j in range(-1, m):                  # j = posición del fallo (-1: coincidencia completa)
        k = 1
        while k <= m:
            encaja = True
            for i in range(j + 1, m):       # cada carácter del sufijo bueno...
                if i - k >= 0 and patron[i - k] != patron[i]:
                    encaja = False          # ...debe coincidir con el patrón desplazado k
                    break
            if encaja:
                break
            k += 1
        sufijo[j + 1] = k
    return sufijo


def boyer_moore_buscar(texto, patron, ultima, sufijo):
    """Alinea el patrón con el texto y compara de DERECHA a IZQUIERDA.
    Cuando hay un fallo, desplaza el patrón lo máximo que permitan las dos reglas.
    Peor caso O(n·m); en texto normal suele comparar mucho menos que n caracteres."""
    n, m = len(texto), len(patron)
    posiciones, comparaciones = [], 0
    s = 0                                   # desplazamiento del patrón sobre el texto
    while s <= n - m:
        j = m - 1
        while j >= 0:
            comparaciones += 1
            if patron[j] != texto[s + j]:
                break
            j -= 1
        if j < 0:                           # coincidieron todos
            posiciones.append(s)
            s += sufijo[0]
        else:
            salto_malo = j - ultima.get(texto[s + j], -1)
            salto_bueno = sufijo[j + 1]
            s += max(salto_malo, salto_bueno, 1)
    return posiciones, comparaciones


def boyer_moore(texto, patron):
    return boyer_moore_buscar(texto, patron, tabla_caracter_malo(patron), tabla_sufijo_bueno(patron))


# ===========================================================================
# 3. Rabin-Karp (aritmética modular y hash rodante)
# ===========================================================================
BASE = 256                                  # d: tamaño del alfabeto (un byte por carácter)
PRIMO = 1_000_000_007                       # q: número primo grande -> pocas colisiones


def rabin_karp_preprocesar(patron, base=BASE, primo=PRIMO):
    """Calcula el hash del patrón y h = base^(m-1) mod primo (método de Horner).
    hash('abc') = (a·base² + b·base + c) mod primo. Costo: O(m)."""
    m = len(patron)
    h = 1
    for _ in range(m - 1):
        h = (h * base) % primo
    hash_patron = 0
    for c in patron:
        hash_patron = (base * hash_patron + ord(c)) % primo
    return hash_patron, h


def rabin_karp_buscar(texto, patron, hash_patron, h, base=BASE, primo=PRIMO):
    """Compara hashes en vez de cadenas. El hash de cada ventana del texto se
    obtiene del anterior en O(1) (hash rodante): se quita el carácter que sale
    y se agrega el que entra. Solo si los hashes coinciden se comparan los
    caracteres, porque dos cadenas distintas pueden tener el mismo hash (colisión).
    Costo esperado O(n + m); peor caso O(n·m) si hay muchas colisiones.
    Devuelve además cuántas colisiones (falsos positivos) hubo."""
    n, m = len(texto), len(patron)
    posiciones, comparaciones, colisiones = [], 0, 0
    if m > n:
        return posiciones, comparaciones, colisiones
    hash_ventana = 0
    for i in range(m):                      # hash de la primera ventana
        hash_ventana = (base * hash_ventana + ord(texto[i])) % primo
    for s in range(n - m + 1):
        if hash_ventana == hash_patron:     # posible coincidencia: se verifica
            j = 0
            while j < m:
                comparaciones += 1
                if texto[s + j] != patron[j]:
                    break
                j += 1
            if j == m:
                posiciones.append(s)
            else:
                colisiones += 1             # mismo hash, distinta cadena
        if s < n - m:                       # hash rodante hacia la siguiente ventana
            hash_ventana = (base * (hash_ventana - ord(texto[s]) * h) + ord(texto[s + m])) % primo
    return posiciones, comparaciones, colisiones


def rabin_karp(texto, patron, base=BASE, primo=PRIMO):
    hash_patron, h = rabin_karp_preprocesar(patron, base, primo)
    posiciones, comparaciones, _ = rabin_karp_buscar(texto, patron, hash_patron, h, base, primo)
    return posiciones, comparaciones
