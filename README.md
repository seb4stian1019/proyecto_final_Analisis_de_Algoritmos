# Análisis de algoritmos en el contexto de la bibliometría (Proyecto final 2026-2)

Similitud textual, agrupamiento jerárquico y búsqueda de patrones sobre los abstracts
de 20 artículos científicos. Todos los algoritmos están programados a mano.

**Autores:** Samuel Salgado Figueroa y Sebastián Amaya Castaño
**Curso:** Análisis de Algoritmos, Universidad del Quindío

## Estructura, en el orden en que se lee

| Orden | Carpeta | Qué contiene |
|---|---|---|
| 1 | `articulos/` | Los 20 PDF del corpus (01 a 20) |
| 2 | `paso1_corpus/` | Paso 1: extrae título, autores y abstract de cada PDF y verifica la extracción |
| 3 | `req1_similitud/` | Requerimiento 1: 4 algoritmos clásicos de similitud y 2 modelos de IA |
| 4 | `req2_agrupamiento/` | Requerimiento 2: agrupamiento jerárquico con 3 criterios y dendrogramas |
| 5 | `req3_busqueda/` | Requerimiento 3: KMP, Boyer-Moore y Rabin-Karp, y medición de tiempos |
| 6 | `resultados/` | Lo que genera cada paso, con el prefijo de su paso: `corpus_*`, `req1_*`, `req2_*`, `req3_*` |
| — | `main.py` | Ejecuta todo en orden |

Cada carpeta tiene su propio `README.md` con sus archivos en orden de lectura. Dentro de cada
requerimiento el orden es siempre el mismo: primero los algoritmos, luego sus pruebas, después
los scripts que los aplican a los 20 abstracts y al final el caso de estudio paso a paso.

Los requerimientos se apoyan en los anteriores: el Requerimiento 2 reutiliza el TF-IDF y el coseno
de `req1_similitud/similitud.py`, y la verificación del Paso 1 usa el KMP de `req3_busqueda/busqueda.py`.

## Cómo ejecutarlo

1. Instalar las dependencias (una sola vez): `pip install -r requirements.txt`
2. Solo para recalcular los vectores de IA: `pip install -r requirements-ia.txt`
3. Ejecutar todo en orden, desde la raíz del proyecto: `python main.py`

Cada script también se puede ejecutar por separado, siempre desde la raíz y con `-m`
(carpeta.archivo, sin `.py`), por ejemplo:

- `python -m req1_similitud.comparar 11 16` compara dos (o más) artículos con los 6 algoritmos.
- `python -m req2_agrupamiento.dendrogramas` agrupa los 20 abstracts y dibuja los dendrogramas.
- `python -m req3_busqueda.buscar_patron "generative ai"` busca un patrón en los 20 abstracts.
- `python -m req3_busqueda.tiempos` vuelve a medir los tiempos en el equipo actual.

## Librerías y para qué se usan

| Librería | Uso | ¿Implementa algún algoritmo pedido? |
|---|---|---|
| pdfminer.six | Leer el texto de los PDF, con el tamaño y la posición de cada carácter | No |
| matplotlib | Dibujar las gráficas y las líneas de los dendrogramas (las coordenadas se calculan en `req2_agrupamiento/clustering.py`) | No |
| sentence-transformers | Solo en `req1_similitud/embeddings.py`: convertir cada abstract en un vector con el modelo MiniLM (la similitud se calcula a mano) | No |
