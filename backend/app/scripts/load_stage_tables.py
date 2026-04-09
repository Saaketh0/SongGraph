from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.scripts.run_phase1 import run_ingestion


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(
        description="Load song metadata and neighbors into dedicated Phase 1B staging tables."
    )
    parser.add_argument(
        "--parquet-path",
        default=str(repo_root / "final_song_data.parquet"),
        help="Path to song metadata parquet file.",
    )
    parser.add_argument(
        "--similarity-csv-path",
        default=str(repo_root / "song_similarities.csv"),
        help="Path to similarity CSV containing sim_song_1..sim_song_5 columns.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validation only and skip database writes.",
    )
    parser.add_argument(
        "--ingestion-engine",
        choices=["orm", "copy"],
        default="orm",
        help="Stage-load implementation engine. 'copy' uses PostgreSQL COPY.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        "Deprecated: use `python -m app.scripts.run_phase1 load-stage` or `validate` instead.",
        file=sys.stderr,
    )
    result = run_ingestion(
        validate_only=args.validate_only,
        parquet_path=str(Path(args.parquet_path)),
        similarity_csv_path=str(Path(args.similarity_csv_path)),
        ingestion_engine=args.ingestion_engine,
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
