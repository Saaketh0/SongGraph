from __future__ import annotations

import json
from pathlib import Path

from song_cleaning.tempo_imputation import impute_tempo_file


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "finalv1.parquet"
OUTPUT_PATH = ROOT / "finalv2.parquet"
METADATA_PATH = ROOT / "outputs" / "profiling" / "finalv2_tempo_imputation.json"


def main() -> None:
    result = impute_tempo_file(INPUT_PATH, OUTPUT_PATH)
    payload = {
        "input_path": str(INPUT_PATH),
        "output_path": str(result.output_path),
        "missing_rows_imputed": result.missing_rows,
        "metrics": result.metrics,
    }
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
