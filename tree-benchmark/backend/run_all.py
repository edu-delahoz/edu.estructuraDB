"""Ejecuta el flujo completo del backend: dataset + benchmark."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Define argumentos de ejecución del flujo completo."""
    parser = argparse.ArgumentParser(description="Ejecutar pipeline backend completo.")
    parser.add_argument(
        "--mode",
        choices=("ordered", "random"),
        default="ordered",
        help="Modo de generación de dataset para users.csv.",
    )
    return parser.parse_args()


def run_command(command: list[str], cwd: Path) -> None:
    """Ejecuta un comando y falla si devuelve código distinto de cero."""
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    """Orquesta generación de dataset y benchmark."""
    args = parse_args()
    backend_dir = Path(__file__).resolve().parent

    print(f"[1/2] Generando dataset en modo '{args.mode}'...")
    run_command([sys.executable, str(backend_dir / "generate_dataset.py"), "--mode", args.mode], backend_dir)

    print("[2/2] Ejecutando benchmark...")
    run_command([sys.executable, str(backend_dir / "benchmark.py")], backend_dir)

    results_file = backend_dir / "results" / "results.json"
    print(f"Listo. Resultados disponibles en: {results_file}")


if __name__ == "__main__":
    main()