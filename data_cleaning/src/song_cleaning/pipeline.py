from pathlib import Path

from .columns import ALL_COLUMNS, get_column_groups
from .defaults import apply_default_fills
from .deterministic_fill import run_deterministic_fill
from .invalid_values import convert_invalid_values_to_null
from .io import read_parquet, write_json, write_parquet
from .normalize import normalize_text_columns
from .profile import build_profile


def run_pre_imputation_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> dict:
    df = read_parquet(input_path, columns=ALL_COLUMNS)

    raw_profile = build_profile(df)

    normalized = normalize_text_columns(df)
    invalid_cleaned, invalid_to_null_counts = convert_invalid_values_to_null(normalized)
    deterministically_filled, fill_stats = run_deterministic_fill(invalid_cleaned)
    default_filled, default_fill_counts = apply_default_fills(deterministically_filled)

    final_profile = build_profile(default_filled)

    report = {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "report_path": str(report_path),
        "column_groups": get_column_groups(),
        "raw_profile": raw_profile,
        "invalid_to_null_counts": invalid_to_null_counts,
        "deterministic_fill": fill_stats,
        "default_fill_counts": default_fill_counts,
        "final_profile": final_profile,
    }

    write_parquet(default_filled, output_path)
    write_json(report, report_path)

    return report
