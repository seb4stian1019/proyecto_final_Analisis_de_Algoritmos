# Requerimiento 3: búsqueda de patrones

Busca un patrón en los 20 abstracts con KMP, Boyer-Moore y Rabin-Karp, programados a mano, y compara el tiempo de preprocesamiento con el de búsqueda. La explicación completa está en la sección 4 del documento.

## Archivos, en orden de lectura

| Orden | Archivo | Qué hace |
|---|---|---|
| 1 | `busqueda.py` | Fuerza bruta (referencia), KMP, Boyer-Moore y Rabin-Karp, cada uno separado en preprocesamiento y búsqueda |
| 2 | `pruebas.py` | Casos calculados a mano y 20.000 casos aleatorios contra la fuerza bruta |
| 3 | `buscar_patron.py` | Busca un patrón del usuario en los 20 abstracts y verifica que los tres algoritmos coincidan |
| 4 | `caso_estudio.py` | Traza paso a paso del caso de estudio → `resultados/req3_caso_estudio.json` |
| 5 | `tiempos.py` | Mide preprocesamiento y búsqueda por separado → `resultados/req3_tiempos_*.csv`, gráficas y `resultados/req3_entorno.txt` |

## Cómo ejecutarlo

Desde la raíz del proyecto (no desde esta carpeta):

```
python -m req3_busqueda.pruebas
python -m req3_busqueda.buscar_patron "generative ai"
python -m req3_busqueda.caso_estudio
python -m req3_busqueda.tiempos
```