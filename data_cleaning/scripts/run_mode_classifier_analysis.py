from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from song_cleaning.mode_classifier_analysis import run_mode_analysis


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "finalv3.parquet"
OUTPUT_CSV = ROOT / "outputs" / "profiling" / "mode_classifier_analysis.csv"
OUTPUT_JSON = ROOT / "outputs" / "profiling" / "mode_classifier_analysis.json"


def main() -> None:
    result = run_mode_analysis(INPUT_PATH)
    frame = pd.DataFrame(result.results)
    frame = frame.sort_values(
        ["f1_macro", "recall_zero", "predicted_zero_rate_missing", "accuracy"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT_CSV, index=False)

    payload = {
        "input_path": str(INPUT_PATH),
        "missing_rows": result.missing_rows,
        "top_results": frame.head(10).to_dict(orient="records"),
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2))

    print(frame.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
