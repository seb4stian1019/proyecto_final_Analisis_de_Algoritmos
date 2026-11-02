# Análisis de algoritmos en el contexto de la bibliometría (Proyecto final 2026-2)

Similitud textual, agrupamiento jerárquico y búsqueda de patrones sobre los abstracts
de 20 artículos científicos. Todos los algoritmos están programados a mano.

**Autores:** Samuel Salgado Figueroa y Sebastián Amaya Castaño  
**Curso:** Análisis de Algoritmos, Universidad del Quindío

## Cómo ejecutarlo

1. Instalar las dependencias (una sola vez): `pip install -r requirements.txt`
2. Solo la primera vez que se calculan los vectores de IA: `pip install -r requirements-ia.txt`
3. Copiar los 20 PDF en la carpeta `articulos/`
4. Ejecutar todo en orden: `python main.py`

También se puede ejecutar cada script por separado, por ejemplo:

- `python req1_similitud.py 11 16` compara dos (o más) artículos con los 6 algoritmos.
- `python req3_busqueda.py "generative ai"` busca un patrón en los 20 abstracts.
- `python req3_tiempos.py` vuelve a medir los tiempos en el equipo actual.

## Librerías y para qué se usan

| Librería | Uso | ¿Implementa algún algoritmo pedido? |
|---|---|---|
| pdfminer.six | Leer el texto de los PDF, con el tamaño y la posición de cada carácter | No |
| matplotlib | Dibujar las gráficas | No |
| sentence-transformers | Solo en `req1_embeddings.py`: convertir cada abstract en un vector con el modelo MiniLM (la similitud se calcula a mano) | No |

## Estructura

| Archivo | Qué hace | Estado |
|---|---|---|
| `paso1_corpus.py` | Extrae título, autores y abstract de cada PDF → `resultados/corpus.json` | Listo |
| `datos.py` | Lee `resultados/corpus.json` para los demás módulos | Listo |
| `busqueda.py` | Fuerza bruta (referencia), KMP, Boyer-Moore y Rabin-Karp, cada uno separado en preprocesamiento y búsqueda | Listo |
| `req3_busqueda.py` | Busca un patrón del usuario en los 20 abstracts y verifica que los tres algoritmos coincidan | Listo |
| `req3_caso_estudio.py` | Traza paso a paso del caso de estudio → `resultados/req3_caso_estudio.json` | Listo |
| `req3_tiempos.py` | Mide preprocesamiento y búsqueda por separado → CSV y gráficas en `resultados/` | Listo |
| `pruebas_busqueda.py` | Casos calculados a mano y 20.000 casos aleatorios contra la fuerza bruta | Listo |
| `main.py` | Ejecuta todo en orden | Listo |
| `similitud.py` | Preprocesamiento, Levenshtein, LCS, Jaccard, TF-IDF y coseno, matriz de similitud | Listo |
| `pruebas_similitud.py` | Casos calculados a mano y 3.000 pares aleatorios contra la definición recursiva | Listo |
| `req1_embeddings.py` | Vectores de los 20 abstracts con GloVe y MiniLM → `resultados/req1_embeddings.json` | Listo |
| `req1_similitud.py` | Compara dos o más artículos con los 6 algoritmos; sin argumentos, matrices 20 x 20 | Listo |
| `req1_caso_estudio.py` | Caso de estudio paso a paso (artículos 11 y 16) → `resultados/req1_caso_estudio.json` | Listo |
| Requerimiento 2 | Agrupamiento jerárquico y dendrogramas | Pendiente |
| Requerimiento 4 | Aplicación desplegada | Pendiente |
