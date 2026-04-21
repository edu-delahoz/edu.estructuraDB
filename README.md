# edu.estructuraDB

Proyecto de comparativa de estructuras de datos (ABB vs Árbol B+) con un pipeline de backend en Python y un dashboard de visualización en Next.js.

---

## Requisitos previos

| Herramienta | Versión mínima | Notas |
|-------------|---------------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | incluido con Node.js |

> Todos los comandos de Python deben ejecutarse **desde la raíz del repositorio** salvo que se indique lo contrario.

---

## Estructura del proyecto

```
edu.estructuraDB/
├── tree-benchmark/
│   ├── backend/
│   │   ├── generate_dataset.py   # Genera el dataset CSV
│   │   ├── abb.py                # Implementación del ABB
│   │   ├── bplus.py              # Implementación del Árbol B+
│   │   ├── test_abb_dataset.py   # Validación ABB con dataset real
│   │   ├── test_bplus_dataset.py # Validación B+ con dataset real
│   │   ├── benchmark.py          # Benchmark de rendimiento
│   │   ├── run_all.py            # Pipeline completo (dataset + benchmark)
│   │   └── data/
│   │       └── users.csv         # Dataset generado (1 000 usuarios)
│   └── frontend/                 # Dashboard Next.js
│       └── ...
```

---

## Guía de ejecución paso a paso

### 1. Generar el dataset

El dataset se puede generar en dos modos:

**Modo ordenado** (IDs 1 → 1 000, expone el peor caso del ABB):

```bash
python tree-benchmark/backend/generate_dataset.py --mode ordered
```

**Modo aleatorio** (IDs mezclados con semilla fija `42`):

```bash
python tree-benchmark/backend/generate_dataset.py --mode random
```

Ambos modos crean el archivo `tree-benchmark/backend/data/users.csv` con **1 000 registros** únicos (id, nombre, email, edad).

---

### 2. Probar el ABB manualmente

Ejecuta una demostración rápida de inserción, búsqueda y recorrido in-order con datos de ejemplo:

```bash
python tree-benchmark/backend/abb.py
```

---

### 3. Probar el Árbol B+ manualmente

Ejecuta una demostración rápida de inserción, búsqueda exacta y búsqueda por rango con datos de ejemplo:

```bash
python tree-benchmark/backend/bplus.py
```

Validar sintaxis del archivo antes de ejecutar:

```bash
python -m py_compile tree-benchmark/backend/bplus.py
```

---

### 4. Validar el ABB con el dataset real

Primero asegúrate de que el dataset esté generado (paso 1), luego:

```bash
python tree-benchmark/backend/generate_dataset.py --mode ordered
python tree-benchmark/backend/test_abb_dataset.py
```

El script valida: cantidad de registros, búsquedas positivas, búsquedas negativas y recorrido in-order ordenado.

---

### 5. Validar el Árbol B+ con el dataset real

```bash
python tree-benchmark/backend/generate_dataset.py --mode ordered
python tree-benchmark/backend/test_bplus_dataset.py
```

El script valida: cantidad de registros, búsquedas exactas, búsquedas negativas y búsqueda por rango.

---

### 6. Ejecutar el benchmark

El benchmark mide tiempos de construcción, búsqueda exacta y búsqueda por rango para ABB y B+ en ambos escenarios (ordered y random). Guarda los resultados en `tree-benchmark/backend/results/results.json`.

```bash
python tree-benchmark/backend/generate_dataset.py --mode ordered
python tree-benchmark/backend/benchmark.py
```

---

### 7. Pipeline completo con `run_all.py` ⭐

Ejecuta todo de una vez: generación de dataset y benchmark.

**Modo ordenado:**

```bash
python tree-benchmark/backend/run_all.py --mode ordered
```

**Modo aleatorio:**

```bash
python tree-benchmark/backend/run_all.py --mode random
```

Al finalizar, los resultados quedan en:

```
tree-benchmark/backend/results/results.json
```

---

### 8. Visualizar resultados en el frontend

Después de ejecutar `run_all.py`, puedes visualizar los resultados en un dashboard interactivo en lugar de leer el JSON directamente.

```bash
cd tree-benchmark/frontend
npm install        # solo la primera vez
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en el navegador para ver el panel de resultados con tablas y gráficas comparativas de ABB vs B+.

> El frontend lee automáticamente `tree-benchmark/backend/results/results.json`. Si ejecutas `run_all.py` de nuevo, recarga la página para ver los nuevos resultados.

---

## Flujo recomendado completo

```bash
# 1. Generar dataset y ejecutar benchmark
python tree-benchmark/backend/run_all.py --mode ordered

# 2. Ver resultados en el navegador
cd tree-benchmark/frontend
npm install   # solo la primera vez
npm run dev
# Abre http://localhost:3000
```

---

## Notas

- Los scripts de backend no tienen dependencias externas (solo la biblioteca estándar de Python).
- El frontend requiere Node.js ≥ 18. Las dependencias (`node_modules`) **no** están incluidas en el repositorio; ejecuta `npm install` antes de `npm run dev`.
- El dataset se regenera cada vez que se ejecuta `generate_dataset.py`; el modo `ordered` es el recomendado para observar las diferencias de rendimiento más marcadas entre ABB y B+.