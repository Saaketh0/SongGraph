from __future__ import annotations

import json
from pathlib import Path

from song_cleaning.final_dataset_postprocess import postprocess_final_dataset_file


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "finalv2.parquet"
OUTPUT_PATH = ROOT / "finalv3.parquet"
METADATA_PATH = ROOT / "outputs" / "profiling" / "finalv3_postprocess.json"


def main() -> None:
    result = postprocess_final_dataset_file(INPUT_PATH, OUTPUT_PATH)
    payload = {
        "input_path": str(INPUT_PATH),
        "output_path": str(OUTPUT_PATH),
        **result,
    }
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
