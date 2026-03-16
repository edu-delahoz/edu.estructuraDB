# Instrucciones del proyecto tree-benchmark

Quiero construir un proyecto académico para comparar un árbol ABB y un árbol B+ en Python.

## Objetivo
- Generar un dataset de 10.000 usuarios con campos: `id`, `nombre`, `email`, `edad`.
- Guardarlo en CSV.
- Crear dos estructuras: ABB y B+.
- Medir tiempos de:
  1) construcción de la estructura
  2) búsqueda exacta por ID
  3) búsqueda por rango de IDs (solo donde aplique)
- Comparar inserción con IDs en orden y IDs aleatorios.
- Medir búsquedas con lotes de 100, 1000, 2000 y 5000 IDs aleatorios.
- Usar `time.perf_counter_ns()`.
- Repetir cada prueba 30 veces.
- Guardar resultados agregados en JSON con promedio, mediana, mínimo, máximo y desviación estándar.
- No mezclar frontend con la medición.
- El frontend será Next.js y solo mostrará resultados.
