"""Genera un dataset reproducible de usuarios y lo exporta a CSV."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

TOTAL_USERS = 10_000
MIN_AGE = 18
MAX_AGE = 60
SEED = 42
OUTPUT_FILE = "users.csv"


def parse_args() -> argparse.Namespace:
    """Obtiene argumentos de ejecución."""
    parser = argparse.ArgumentParser(description="Generar dataset de usuarios.")
    parser.add_argument(
        "--mode",
        choices=("ordered", "random"),
        required=True,
        help="Orden de IDs: ascendente (ordered) o mezclado (random).",
    )
    return parser.parse_args()


def output_path() -> Path:
    """Devuelve la ruta de salida y crea la carpeta si falta."""
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / OUTPUT_FILE


def build_ids(mode: str) -> list[int]:
    """Construye IDs únicos según el modo indicado."""
    ids = list(range(1, TOTAL_USERS + 1))
    if mode == "random":
        random.Random(SEED).shuffle(ids)
    return ids


def build_user_name(user_id: int) -> str:
    """Crea un nombre sintético simple a partir del ID."""
    return f"Usuario {user_id:05d}"


def build_email(user_id: int) -> str:
    """Crea un email único y reproducible."""
    return f"usuario{user_id:05d}@example.com"


def generate_rows(ids: list[int]) -> list[dict[str, str | int]]:
    """Genera filas del dataset con id, nombre, email y edad."""
    rng = random.Random(SEED)
    rows: list[dict[str, str | int]] = []

    for user_id in ids:
        rows.append(
            {
                "id": user_id,
                "nombre": build_user_name(user_id),
                "email": build_email(user_id),
                "edad": rng.randint(MIN_AGE, MAX_AGE),
            }
        )

    return rows


def validate_rows(rows: list[dict[str, str | int]], mode: str) -> None:
    """Ejecuta validaciones básicas del dataset."""
    if len(rows) != TOTAL_USERS:
        raise ValueError("El dataset no contiene 10.000 registros.")

    ids = [int(row["id"]) for row in rows]
    emails = [str(row["email"]) for row in rows]
    ages = [int(row["edad"]) for row in rows]

    if len(set(ids)) != TOTAL_USERS:
        raise ValueError("Hay IDs duplicados en el dataset.")
    if len(set(emails)) != TOTAL_USERS:
        raise ValueError("Hay emails duplicados en el dataset.")
    if not all(MIN_AGE <= age <= MAX_AGE for age in ages):
        raise ValueError("Se detectó una edad fuera del rango 18-60.")

    if mode == "ordered" and ids != sorted(ids):
        raise ValueError("En modo ordered los IDs deben estar en orden ascendente.")


def write_csv(rows: list[dict[str, str | int]], destination: Path) -> None:
    """Escribe las filas en el archivo CSV final."""
    headers = ["id", "nombre", "email", "edad"]
    with destination.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Orquesta la generación y persistencia del dataset."""
    args = parse_args()
    ids = build_ids(mode=args.mode)
    rows = generate_rows(ids=ids)
    validate_rows(rows=rows, mode=args.mode)

    destination = output_path()
    write_csv(rows=rows, destination=destination)

    print(f"Se generaron {len(rows)} registros en: {destination}")


if __name__ == "__main__":
    main()