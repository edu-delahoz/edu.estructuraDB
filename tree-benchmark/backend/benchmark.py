"""Benchmark reproducible para comparar ABB y B+ con dataset de usuarios."""

from __future__ import annotations

import csv
import json
import random
import time
from pathlib import Path
from statistics import mean, median, pstdev

from abb import ABBTree
from bplus import BPlusTree

TOTAL_REPEATS = 5
WARMUP_REPEATS = 1
RANDOM_SEED = 42
SEARCH_BATCH_SIZES = (100, 1000, 2000)
RANGE_WINDOW = 100


def data_path() -> Path:
    """Retorna la ruta del dataset CSV."""
    return Path(__file__).resolve().parent / "data" / "users.csv"


def results_path() -> Path:
    """Retorna la ruta del JSON de resultados y crea el directorio si falta."""
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir / "results.json"


def load_users(path: Path) -> list[dict]:
    """Carga usuarios desde CSV en memoria."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {path}")

    users: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(
                {
                    "id": int(row["id"]),
                    "nombre": row["nombre"],
                    "email": row["email"],
                    "edad": int(row["edad"]),
                }
            )
    return users


def build_scenarios(users: list[dict]) -> dict[str, list[dict]]:
    """Prepara dataset en orden y en orden aleatorio reproducible."""
    ordered_users = sorted(users, key=lambda user: int(user["id"]))
    random_users = list(ordered_users)
    random.Random(RANDOM_SEED).shuffle(random_users)
    return {"ordered": ordered_users, "random": random_users}


def create_tree(structure: str):
    """Crea una instancia de ABB o B+ según nombre de estructura."""
    if structure == "abb":
        return ABBTree()
    if structure == "bplus":
        return BPlusTree(order=4)
    raise ValueError(f"Estructura no soportada: {structure}")


def build_exact_batches(ids: list[int]) -> dict[int, list[list[int]]]:
    """Genera lotes de IDs para búsquedas exactas por tamaño de lote."""
    rng = random.Random(RANDOM_SEED)
    batches: dict[int, list[list[int]]] = {}
    for size in SEARCH_BATCH_SIZES:
        batches[size] = [rng.sample(ids, size) for _ in range(TOTAL_REPEATS)]
    return batches


def build_range_batches(ids: list[int]) -> list[tuple[int, int]]:
    """Genera rangos [inicio, fin] reproducibles para range_search."""
    rng = random.Random(RANDOM_SEED + 1)
    max_start_index = max(0, len(ids) - RANGE_WINDOW)
    ranges: list[tuple[int, int]] = []
    for _ in range(TOTAL_REPEATS):
        start_index = rng.randint(0, max_start_index)
        start_id = ids[start_index]
        end_id = ids[min(len(ids) - 1, start_index + RANGE_WINDOW - 1)]
        ranges.append((start_id, end_id))
    return ranges


def aggregate_stats(
    times_ns: list[int],
    *,
    structure: str,
    dataset_mode: str,
    operation: str,
    repeats: int,
    batch_size: int | None = None,
) -> dict:
    """Calcula estadísticas agregadas para una serie de tiempos."""
    result = {
        "structure": structure,
        "dataset_mode": dataset_mode,
        "operation": operation,
        "repeats": repeats,
        "average_ns": mean(times_ns),
        "median_ns": median(times_ns),
        "min_ns": min(times_ns),
        "max_ns": max(times_ns),
        "stddev_ns": pstdev(times_ns),
    }
    if batch_size is not None:
        result["batch_size"] = batch_size
    return result


def build_tree_for_search(users: list[dict], structure: str):
    """Construye una estructura una vez para mediciones de búsqueda."""
    tree = create_tree(structure)
    tree.bulk_insert(users)
    return tree


def warm_up_operation(users: list[dict], structure: str, exact_batch: list[int], range_batch: tuple[int, int]) -> None:
    """Warm-up real de construcción y consultas para un escenario."""
    for _ in range(WARMUP_REPEATS):
        tree = create_tree(structure)
        tree.bulk_insert(users)
        for user_id in exact_batch:
            tree.search(user_id)
        if structure == "bplus":
            assert isinstance(tree, BPlusTree)
            tree.range_search(range_batch[0], range_batch[1])


def benchmark_construction(users: list[dict], structure: str, dataset_mode: str) -> dict:
    """Mide construcción de estructura para un escenario dado."""
    times_ns: list[int] = []
    for _ in range(TOTAL_REPEATS):
        start = time.perf_counter_ns()
        tree = create_tree(structure)
        tree.bulk_insert(users)
        end = time.perf_counter_ns()
        times_ns.append(end - start)

    return aggregate_stats(
        times_ns,
        structure=structure,
        dataset_mode=dataset_mode,
        operation="build",
        repeats=TOTAL_REPEATS,
    )


def benchmark_exact_search(
    tree,
    structure: str,
    dataset_mode: str,
    batches_by_size: dict[int, list[list[int]]],
) -> list[dict]:
    """Mide búsquedas exactas por lotes sin incluir construcción."""
    results: list[dict] = []
    for size in SEARCH_BATCH_SIZES:
        times_ns: list[int] = []
        for batch in batches_by_size[size]:
            start = time.perf_counter_ns()
            for user_id in batch:
                tree.search(user_id)
            end = time.perf_counter_ns()
            times_ns.append(end - start)

        results.append(
            aggregate_stats(
                times_ns,
                structure=structure,
                dataset_mode=dataset_mode,
                operation="exact_search",
                repeats=TOTAL_REPEATS,
                batch_size=size,
            )
        )
    return results


def benchmark_range_search_bplus(tree: BPlusTree, dataset_mode: str, ranges: list[tuple[int, int]]) -> dict:
    """Mide búsqueda por rango para B+ sin incluir construcción."""
    times_ns: list[int] = []
    for start_id, end_id in ranges:
        start = time.perf_counter_ns()
        tree.range_search(start_id, end_id)
        end = time.perf_counter_ns()
        times_ns.append(end - start)

    return aggregate_stats(
        times_ns,
        structure="bplus",
        dataset_mode=dataset_mode,
        operation="range_search",
        repeats=TOTAL_REPEATS,
        batch_size=RANGE_WINDOW,
    )


def run_benchmark(users: list[dict]) -> dict:
    """Ejecuta benchmark completo para ABB y B+ en ordered/random."""
    scenarios = build_scenarios(users)
    ids = sorted(user["id"] for user in users)
    exact_batches = build_exact_batches(ids)
    range_batches = build_range_batches(ids)

    results: list[dict] = []
    for dataset_mode, scenario_users in scenarios.items():
        for structure in ("abb", "bplus"):
            # Warm-up por estructura y escenario para estabilizar mediciones.
            warm_up_operation(
                scenario_users,
                structure,
                exact_batches[SEARCH_BATCH_SIZES[0]][0],
                range_batches[0],
            )

            results.append(benchmark_construction(scenario_users, structure, dataset_mode))

            tree = build_tree_for_search(scenario_users, structure)
            results.extend(benchmark_exact_search(tree, structure, dataset_mode, exact_batches))

            if structure == "bplus":
                assert isinstance(tree, BPlusTree)
                results.append(benchmark_range_search_bplus(tree, dataset_mode, range_batches))

    return {
        "metadata": {
            "seed": RANDOM_SEED,
            "repeats": TOTAL_REPEATS,
            "warmup_repeats": WARMUP_REPEATS,
            "search_batch_sizes": list(SEARCH_BATCH_SIZES),
            "range_window_ids": RANGE_WINDOW,
            "notes": [
                "build mide creación+inserción",
                "exact_search y range_search no incluyen carga de CSV ni construcción",
                "range_search se mide solo para bplus",
            ],
        },
        "results": results,
    }


def export_results(payload: dict, destination: Path) -> None:
    """Guarda el JSON de resultados con formato legible."""
    with destination.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def main() -> None:
    """Punto de entrada del benchmark."""
    users = load_users(data_path())
    payload = run_benchmark(users)
    destination = results_path()
    export_results(payload, destination)
    print(f"Benchmark completado. Resultados guardados en: {destination}")


if __name__ == "__main__":
    main()