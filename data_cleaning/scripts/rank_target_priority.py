from pathlib import Path
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "outputs" / "cleaned" / "songs_pre_imputation_with_missingness_flags.parquet"
OUTPUT_JSON = ROOT / "outputs" / "profiling" / "target_priority_report.json"
OUTPUT_CSV = ROOT / "outputs" / "profiling" / "target_priority_report.csv"

REGRESSION_TARGETS = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
]

CLASSIFICATION_TARGETS = [
    "key",
    "mode",
]

TARGET_COLUMNS = REGRESSION_TARGETS + CLASSIFICATION_TARGETS

BASE_FEATURE_POOL = [
    "valence",
    "loudness",
    "danceability",
    "energy",
    "tempo",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "key",
    "mode",
]


def normalize(series: pd.Series) -> pd.Series:
    if series.nunique(dropna=False) <= 1:
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / (series.max() - series.min())


def mean_abs_corr(df: pd.DataFrame, target: str) -> float:
    if target not in REGRESSION_TARGETS:
        return float("nan")

    corr = df[REGRESSION_TARGETS].corr(numeric_only=True)[target].drop(target)
    return float(corr.abs().mean())


def target_priority_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total_rows = len(df)

    for target in TARGET_COLUMNS:
        missing_mask = df[target].isna()
        missing_df = df.loc[missing_mask].copy()
        feature_columns = [column for column in BASE_FEATURE_POOL if column != target]
        missing_features = missing_df[feature_columns]

        missing_count = int(missing_mask.sum())
        missing_pct = missing_count / total_rows
        avg_non_null_fraction = float(missing_features.notna().mean(axis=1).mean()) if missing_count else 1.0
        median_non_null_fraction = float(missing_features.notna().mean(axis=1).median()) if missing_count else 1.0
        zero_signal_rows = int((missing_features.notna().sum(axis=1) == 0).sum()) if missing_count else 0
        mean_abs_target_corr = mean_abs_corr(df, target)

        rows.append(
            {
                "target": target,
                "target_type": "regression" if target in REGRESSION_TARGETS else "classification",
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "avg_non_null_fraction_on_missing_rows": avg_non_null_fraction,
                "median_non_null_fraction_on_missing_rows": median_non_null_fraction,
                "zero_signal_missing_rows": zero_signal_rows,
                "mean_abs_corr_with_other_regression_targets": mean_abs_target_corr,
            }
        )

    result = pd.DataFrame(rows)
    regression_only = result["target_type"].eq("regression")

    result["readiness_score"] = 0.6 * normalize(result["avg_non_null_fraction_on_missing_rows"]) + 0.4 * (
        1 - normalize(result["zero_signal_missing_rows"])
    )

    corr_component = normalize(result["mean_abs_corr_with_other_regression_targets"].fillna(0))
    missing_component = normalize(result["missing_count"])
    result["benefit_score"] = 0.6 * corr_component + 0.4 * missing_component

    result["overall_priority_score"] = result["readiness_score"] * result["benefit_score"]
    result.loc[~regression_only, "overall_priority_score"] = np.nan
    result.loc[result["missing_count"].eq(0), "overall_priority_score"] = np.nan

    return result.sort_values(["overall_priority_score", "missing_count"], ascending=[False, False])


def main() -> None:
    df = pd.read_parquet(DATA_PATH, columns=BASE_FEATURE_POOL)
    table = target_priority_table(df)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "data_path": str(DATA_PATH),
                "notes": [
                    "This ranking is heuristic, not a guarantee of downstream gain.",
                    "Regression targets are ranked by a combination of missing-row feature availability and correlation-based downstream usefulness.",
                    "Classification targets key/mode are listed but not ranked in the regression-first priority score.",
                ],
                "targets": table.to_dict(orient="records"),
            },
            indent=2,
        )
    )
    table.to_csv(OUTPUT_CSV, index=False)

    print(table.to_string(index=False))
    print()
    print("json", OUTPUT_JSON)
    print("csv", OUTPUT_CSV)


if __name__ == "__main__":
    main()
