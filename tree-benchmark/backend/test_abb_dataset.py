"""Valida el ABB usando usuarios cargados desde backend/data/users.csv."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from abb import ABBTree


REQUIRED_FIELDS = ("id", "nombre", "email", "edad")


def dataset_path() -> Path:
    """Retorna la ruta del CSV esperado."""
    return Path(__file__).resolve().parent / "data" / "users.csv"


def load_users(path: Path) -> list[dict]:
    """Carga y convierte usuarios desde CSV a diccionarios tipados."""
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


def build_tree(users: list[dict]) -> ABBTree:
    """Crea un ABB e inserta todos los usuarios."""
    tree = ABBTree()
    tree.bulk_insert(users)
    return tree


def sample_existing_ids(users: list[dict]) -> list[int]:
    """Selecciona IDs reales del dataset para pruebas positivas."""
    if not users:
        return []

    ordered_ids = sorted(user["id"] for user in users)
    last_index = len(ordered_ids) - 1
    middle_index = len(ordered_ids) // 2
    return [ordered_ids[0], ordered_ids[middle_index], ordered_ids[last_index]]


def sample_missing_ids(users: list[dict]) -> list[int]:
    """Construye IDs que no deberían existir en el dataset."""
    if not users:
        return [1]

    ids = [user["id"] for user in users]
    max_id = max(ids)
    return [0, -1, max_id + 1, max_id + 10]


def validate_count(users: list[dict], tree: ABBTree) -> tuple[bool, str]:
    """Valida que la cantidad insertada coincida con el CSV."""
    inorder_users = tree.inorder()
    passed = len(users) == len(inorder_users)
    message = f"conteo CSV={len(users)} / conteo ABB={len(inorder_users)}"
    return passed, message


def validate_existing_search(tree: ABBTree, ids: list[int]) -> tuple[bool, str]:
    """Valida búsquedas exactas para IDs existentes."""
    missing_from_tree: list[int] = []
    for user_id in ids:
        found = tree.search(user_id)
        if found is None or int(found["id"]) != user_id:
            missing_from_tree.append(user_id)

    passed = not missing_from_tree
    message = "IDs existentes encontrados" if passed else f"No encontrados: {missing_from_tree}"
    return passed, message


def validate_missing_search(tree: ABBTree, ids: list[int]) -> tuple[bool, str]:
    """Valida que IDs inexistentes retornen None."""
    unexpected_hits: list[int] = []
    for user_id in ids:
        if tree.search(user_id) is not None:
            unexpected_hits.append(user_id)

    passed = not unexpected_hits
    message = "IDs inexistentes retornan None" if passed else f"Se encontraron IDs inexistentes: {unexpected_hits}"
    return passed, message


def validate_inorder_sorted(tree: ABBTree) -> tuple[bool, str]:
    """Valida que inorder esté ordenado ascendentemente por ID."""
    inorder_ids = [int(user["id"]) for user in tree.inorder()]
    passed = inorder_ids == sorted(inorder_ids)
    message = "inorder() está ordenado ascendentemente" if passed else "inorder() no está ordenado"
    return passed, message


def print_result(label: str, passed: bool, detail: str) -> None:
    """Imprime una validación con formato simple."""
    status = "OK" if passed else "FAIL"
    print(f"[{status}] {label}: {detail}")


def main() -> None:
    """Ejecuta la validación completa del ABB con dataset real."""
    try:
        path = dataset_path()
        users = load_users(path)
        tree = build_tree(users)

        # Evita RecursionError en ABB muy desbalanceados (IDs ordenados).
        sys.setrecursionlimit(max(sys.getrecursionlimit(), len(users) * 3))

        existing_ids = sample_existing_ids(users)
        missing_ids = sample_missing_ids(users)

        checks = [
            ("Cantidad de registros", *validate_count(users, tree)),
            ("Búsqueda de IDs existentes", *validate_existing_search(tree, existing_ids)),
            ("Búsqueda de IDs inexistentes", *validate_missing_search(tree, missing_ids)),
            ("Recorrido in-order", *validate_inorder_sorted(tree)),
        ]

        all_passed = True
        print(f"Dataset cargado desde: {path}")
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