from __future__ import annotations

import json
from pathlib import Path

from song_cleaning.final_dataset_audit import build_audit, load_dataset


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "finalv2.parquet"
OUTPUT_PATH = ROOT / "outputs" / "profiling" / "finalv2_audit.json"


def main() -> None:
    df = load_dataset(INPUT_PATH)
    audit = build_audit(df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit["basic_profile"], indent=2))
    print("---")
    print(json.dumps(audit["metadata_profile"], indent=2))


if __name__ == "__main__":
    main()
