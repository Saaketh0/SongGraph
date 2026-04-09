from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from app.phase1.workflow import Phase1IngestionOptions, run_phase1b_staging_ingestion


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    repo_root = _repo_root()
    parser = argparse.ArgumentParser(description="Consolidated Phase 1 runner (1A migrations + 1B staging ingestion).")
    parser.add_argument(
        "action",
        choices=["migrate", "validate", "load-stage", "all"],
        help="Phase 1 action to run.",
    )
    parser.add_argument(
        "--parquet-path",
        default=str(repo_root / "final_song_data.parquet"),
        help="Path to source parquet file.",
    )
    parser.add_argument(
        "--similarity-csv-path",
        default=str(repo_root / "song_similarities.csv"),
        help="Path to source similarity CSV file.",
    )
    parser.add_argument(
        "--ingestion-engine",
        choices=["orm", "copy"],
        default="orm",
        help="Stage-load implementation engine. 'orm' is default; 'copy' uses PostgreSQL COPY.",
    )
    return parser.parse_args()


def run_migrations() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=_backend_root(),
        check=True,
    )


def run_ingestion(
    validate_only: bool,
    parquet_path: str,
    similarity_csv_path: str,
    ingestion_engine: str = "orm",
) -> dict[str, int | bool | str]:
    return run_phase1b_staging_ingestion(
        Phase1IngestionOptions(
            parquet_path=Path(parquet_path),
            similarity_csv_path=Path(similarity_csv_path),
            validate_only=validate_only,
            ingestion_engine=ingestion_engine,
        )
    )


def main() -> None:
    args = parse_args()

    if args.action == "migrate":
        run_migrations()
        print(json.dumps({"action": "migrate", "status": "ok"}))
        return

    if args.action == "validate":
        result = run_ingestion(
            validate_only=True,
            parquet_path=args.parquet_path,
            similarity_csv_path=args.similarity_csv_path,
            ingestion_engine=args.ingestion_engine,
        )
        print(json.dumps({"action": "validate", **result}))
        return

    if args.action == "load-stage":
        result = run_ingestion(
            validate_only=False,
            parquet_path=args.parquet_path,
            similarity_csv_path=args.similarity_csv_path,
            ingestion_engine=args.ingestion_engine,
        )
        print(json.dumps({"action": "load-stage", **result}))
        return

    run_migrations()
    result = run_ingestion(
        validate_only=False,
        parquet_path=args.parquet_path,
        similarity_csv_path=args.similarity_csv_path,
        ingestion_engine=args.ingestion_engine,
    )
    print(json.dumps({"action": "all", **result}))


if __name__ == "__main__":
    main()
