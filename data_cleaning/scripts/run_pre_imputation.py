import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from song_cleaning.pipeline import run_pre_imputation_pipeline


def main() -> None:
    input_path = ROOT / "final_spotify_master_dataset.parquet"
    output_path = ROOT / "outputs" / "cleaned" / "songs_pre_imputation.parquet"
    report_path = ROOT / "outputs" / "profiling" / "pre_imputation_report.json"

    report = run_pre_imputation_pipeline(
        input_path=input_path,
        output_path=output_path,
        report_path=report_path,
    )

    summary = {
        "output_path": str(output_path),
        "report_path": str(report_path),
        "raw_null_counts": report["raw_profile"]["null_counts"],
        "final_null_counts": report["final_profile"]["null_counts"],
        "invalid_to_null_counts": report["invalid_to_null_counts"],
        "default_fill_counts": report["default_fill_counts"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
