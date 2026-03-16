"""Valida el árbol B+ usando usuarios cargados desde backend/data/users.csv."""

from __future__ import annotations

import csv
from pathlib import Path

from bplus import BPlusTree


REQUIRED_FIELDS = ("id", "nombre", "email", "edad")


def dataset_path() -> Path:
    """Retorna la ruta del CSV esperado."""
    return Path(__file__).resolve().parent / "data" / "users.csv"


def load_users(path: Path) -> list[dict]:
    """Carga usuarios del CSV y convierte tipos básicos."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {path}")

    users: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        missing_headers = [field for field in REQUIRED_FIELDS if field not in (reader.fieldnames or [])]
        if missing_headers:
            raise ValueError(f"El CSV no contiene columnas requeridas: {', '.join(missing_headers)}")

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


def build_tree(users: list[dict]) -> BPlusTree:
    """Crea un B+ tree y realiza inserción masiva."""
    tree = BPlusTree(order=4)
    tree.bulk_insert(users)
    return tree


def sample_existing_ids(users: list[dict]) -> list[int]:
    """Toma IDs reales distribuidos en inicio, medio y final."""
    if not users:
        return []

    ordered_ids = sorted(user["id"] for user in users)
    mid_idx = len(ordered_ids) // 2
    return [ordered_ids[0], ordered_ids[mid_idx], ordered_ids[-1]]


def sample_missing_ids(users: list[dict]) -> list[int]:
    """Construye IDs que no deberían existir en el dataset."""
    if not users:
        return [1]

    max_id = max(user["id"] for user in users)
    return [0, -1, max_id + 1, max_id + 25]


def expected_ids_in_range(users: list[dict], start_id: int, end_id: int) -> list[int]:
    """Obtiene IDs esperados para validar una búsqueda por rango."""
    return sorted(user["id"] for user in users if start_id <= user["id"] <= end_id)


def validate_count(users: list[dict], tree: BPlusTree) -> tuple[bool, str]:
    """Valida que la cantidad insertada coincida con el CSV."""
    if not users:
        count_from_tree = 0
    else:
        ids_from_tree = tree.range_search(min(user["id"] for user in users), max(user["id"] for user in users))
        count_from_tree = len(ids_from_tree)

    passed = len(users) == count_from_tree
    detail = f"conteo CSV={len(users)} / conteo B+={count_from_tree}"
    return passed, detail


def validate_existing_search(tree: BPlusTree, ids: list[int]) -> tuple[bool, str]:
    """Valida búsquedas exactas para IDs existentes."""
    missing: list[int] = []
    for user_id in ids:
        found = tree.search(user_id)
        if found is None or int(found["id"]) != user_id:
            missing.append(user_id)

    passed = not missing
    detail = "IDs existentes encontrados" if passed else f"No encontrados: {missing}"
    return passed, detail


def validate_missing_search(tree: BPlusTree, ids: list[int]) -> tuple[bool, str]:
    """Valida que IDs inexistentes retornen None."""
    unexpected_hits: list[int] = []
    for user_id in ids:
        if tree.search(user_id) is not None:
            unexpected_hits.append(user_id)

    passed = not unexpected_hits
    detail = "IDs inexistentes retornan None" if passed else f"Se encontraron IDs inexistentes: {unexpected_hits}"
    return passed, detail


def validate_range_search(tree: BPlusTree, users: list[dict], start_id: int, end_id: int) -> tuple[bool, str]:
    """Valida exactitud y orden de `range_search` con datos reales."""
    results = tree.range_search(start_id, end_id)
    result_ids = [int(user["id"]) for user in results]
    expected_ids = expected_ids_in_range(users, start_id, end_id)

    ordered_ok = result_ids == sorted(result_ids)
    bounds_ok = all(start_id <= user_id <= end_id for user_id in result_ids)
    exact_match_ok = result_ids == expected_ids

    passed = ordered_ok and bounds_ok and exact_match_ok
    detail = (
        f"rango [{start_id}, {end_id}] -> {len(result_ids)} resultados "
        f"(orden={ordered_ok}, dentro_rango={bounds_ok}, coincide_esperado={exact_match_ok})"
    )
    return passed, detail


def print_result(label: str, passed: bool, detail: str) -> None:
    """Imprime una validación con formato simple."""
    status = "OK" if passed else "FAIL"
    print(f"[{status}] {label}: {detail}")


def main() -> None:
    """Ejecuta la validación completa del árbol B+ con dataset real."""
    try:
        path = dataset_path()
        users = load_users(path)
        tree = build_tree(users)

        existing_ids = sample_existing_ids(users)
        missing_ids = sample_missing_ids(users)

        ordered_ids = sorted(user["id"] for user in users)
        start_id = ordered_ids[len(ordered_ids) // 4]
        end_id = ordered_ids[(len(ordered_ids) * 3) // 4]

        checks = [
            ("Cantidad de registros", *validate_count(users, tree)),
            ("Búsqueda de IDs existentes", *validate_existing_search(tree, existing_ids)),
            ("Búsqueda de IDs inexistentes", *validate_missing_search(tree, missing_ids)),
            ("Búsqueda por rango", *validate_range_search(tree, users, start_id, end_id)),
        ]

        print(f"Dataset cargado desde: {path}")
        all_passed = True
        for label, passed, detail in checks:
            print_result(label, passed, detail)
            all_passed = all_passed and passed

        print("\nResultado general:", "OK" if all_passed else "FAIL")
        if not all_passed:
            raise SystemExit(1)
    except (FileNotFoundError, ValueError) as error:
        print(f"[FAIL] {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()