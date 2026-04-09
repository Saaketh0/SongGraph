from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .invalid_values import collect_invalid_counts


MODELED_FEATURES = [
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

STRING_COLUMNS = ["track_id", "artist_name", "track_name"]
BOUNDED_COLUMNS = [
    "valence",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
]


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def nonempty_string_mask(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().ne("")


def rounded_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return round(float(value), 6)


def to_builtin(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_builtin(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value
    return value


def summarize_numeric(series: pd.Series) -> dict[str, float | None]:
    if len(series) == 0:
        return {
            "count": 0,
            "mean": None,
            "std": None,
            "min": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "max": None,
        }

    quantiles = series.quantile([0.25, 0.5, 0.75])
    return {
        "count": int(len(series)),
        "mean": rounded_float(series.mean()),
        "std": rounded_float(series.std()),
        "min": rounded_float(series.min()),
        "p25": rounded_float(quantiles.loc[0.25]),
        "p50": rounded_float(quantiles.loc[0.5]),
        "p75": rounded_float(quantiles.loc[0.75]),
        "max": rounded_float(series.max()),
    }


def summarize_numeric_by_flag(df: pd.DataFrame, column: str, flag_column: str) -> dict[str, Any]:
    observed = df.loc[df[flag_column] == 0, column].dropna()
    imputed = df.loc[df[flag_column] == 1, column].dropna()

    result: dict[str, Any] = {
        "flagged_rows": int((df[flag_column] == 1).sum()),
        "observed_summary": summarize_numeric(observed),
        "imputed_summary": summarize_numeric(imputed),
        "current_nulls": int(df[column].isna().sum()),
    }

    if column in BOUNDED_COLUMNS:
        result["observed_zero_fraction"] = rounded_float((observed == 0).mean()) if len(observed) else None
        result["observed_one_fraction"] = rounded_float((observed == 1).mean()) if len(observed) else None
        result["imputed_zero_fraction"] = rounded_float((imputed == 0).mean()) if len(imputed) else None
        result["imputed_one_fraction"] = rounded_float((imputed == 1).mean()) if len(imputed) else None
    else:
        result["observed_zero_fraction"] = None
        result["observed_one_fraction"] = None
        result["imputed_zero_fraction"] = None
        result["imputed_one_fraction"] = None

    return result


def summarize_categorical_by_flag(df: pd.DataFrame, column: str, flag_column: str) -> dict[str, Any]:
    observed = df.loc[df[flag_column] == 0, column]
    imputed = df.loc[df[flag_column] == 1, column]
    return {
        "flagged_rows": int((df[flag_column] == 1).sum()),
        "current_nulls": int(df[column].isna().sum()),
        "observed_distribution": {str(k): int(v) for k, v in observed.value_counts(dropna=False).sort_index().items()},
        "imputed_distribution": {str(k): int(v) for k, v in imputed.value_counts(dropna=False).sort_index().items()},
    }


def build_basic_profile(df: pd.DataFrame) -> dict[str, Any]:
    null_counts = df.isna().sum()
    invalid_input = df.copy()
    if "time_signature" not in invalid_input.columns:
        invalid_input["time_signature"] = pd.Series(pd.NA, index=invalid_input.index)
    return {
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "null_counts_nonzero": {column: int(count) for column, count in null_counts[null_counts > 0].items()},
        "invalid_counts": collect_invalid_counts(invalid_input),
    }


def build_metadata_profile(df: pd.DataFrame) -> dict[str, Any]:
    track_id_present = nonempty_string_mask(df["track_id"])
    artist_present = nonempty_string_mask(df["artist_name"])
    track_name_present = nonempty_string_mask(df["track_name"])

    artist_series = df["artist_name"].fillna("").astype(str)
    track_series = df["track_name"].fillna("").astype(str)
    id_series = df["track_id"].fillna("").astype(str)

    return {
        "missing_track_id": int((~track_id_present).sum()),
        "missing_artist_name": int((~artist_present).sum()),
        "missing_track_name": int((~track_name_present).sum()),
        "duplicate_nonempty_track_id_rows": int(df.loc[track_id_present, "track_id"].duplicated().sum()),
        "duplicate_nonempty_track_name_artist_pairs": int(
            df.loc[track_name_present & artist_present, ["track_name", "artist_name"]].duplicated().sum()
        ),
        "artist_name_list_like_prefix": int(artist_series.str.startswith("[").sum()),
        "artist_name_semicolon_count": int(artist_series.str.contains(";", regex=False).sum()),
        "artist_name_comma_count": int(artist_series.str.contains(",", regex=False).sum()),
        "artist_name_leading_trailing_space_count": int((artist_series != artist_series.str.strip()).sum()),
        "track_name_leading_trailing_space_count": int((track_series != track_series.str.strip()).sum()),
        "track_id_leading_trailing_space_count": int((id_series != id_series.str.strip()).sum()),
    }


def build_modeled_feature_profile(df: pd.DataFrame) -> dict[str, Any]:
    profile: dict[str, Any] = {}
    for column in MODELED_FEATURES:
        flag_column = f"{column}_missing"
        if flag_column not in df.columns:
            continue
        if column in {"key", "mode"}:
            profile[column] = summarize_categorical_by_flag(df, column, flag_column)
        else:
            profile[column] = summarize_numeric_by_flag(df, column, flag_column)
    return profile


def build_storage_recommendations(df: pd.DataFrame) -> dict[str, Any]:
    recommendations: dict[str, Any] = {}

    if "key" in df.columns:
        recommendations["key_can_be_int8"] = str(df["key"].dtype) != "int8" and df["key"].dropna().between(0, 11).all()
    if "mode" in df.columns:
        recommendations["mode_can_be_int8"] = str(df["mode"].dtype) != "int8" and df["mode"].dropna().isin([0, 1]).all()

    string_profile: dict[str, bool] = {}
    for column in STRING_COLUMNS:
        string_profile[f"{column}_can_be_string_dtype"] = str(df[column].dtype) != "string"
    recommendations["string_columns"] = string_profile

    return recommendations


def build_audit(df: pd.DataFrame) -> dict[str, Any]:
    audit = {
        "basic_profile": build_basic_profile(df),
        "metadata_profile": build_metadata_profile(df),
        "modeled_feature_profile": build_modeled_feature_profile(df),
        "storage_recommendations": build_storage_recommendations(df),
    }
    return to_builtin(audit)
