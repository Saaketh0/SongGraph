from __future__ import annotations

from pathlib import Path
import ast

import pandas as pd


STRING_COLUMNS = ["track_id", "artist_name", "track_name"]


def normalize_artist_name_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if text == "":
        return pd.NA

    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            parsed = None

        if isinstance(parsed, list):
            parts = [str(part).strip() for part in parsed if str(part).strip()]
            if parts:
                return "; ".join(parts)

        inner = text[1:-1].strip()
        if inner:
            text = inner

    text = "; ".join(part.strip() for part in text.split(";"))
    return text if text else pd.NA


def normalize_artist_name_column(series: pd.Series) -> pd.Series:
    normalized = series.map(normalize_artist_name_value)
    return normalized.astype("string")


def postprocess_final_dataset(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    for column in STRING_COLUMNS:
        if column not in result.columns:
            continue
        if column == "artist_name":
            result[column] = normalize_artist_name_column(result[column])
        else:
            result[column] = result[column].astype("string")

    if "key" in result.columns:
        result["key"] = result["key"].astype("int8")

    if "mode" in result.columns:
        result["mode"] = result["mode"].astype("int8")

    return result


def postprocess_final_dataset_file(input_path: Path, output_path: Path) -> dict[str, int]:
    df = pd.read_parquet(input_path)
    before_bracket_wrappers = int(
        df["artist_name"].fillna("").astype(str).str.strip().str.startswith("[")
        .mul(df["artist_name"].fillna("").astype(str).str.strip().str.endswith("]"))
        .sum()
    )
    processed = postprocess_final_dataset(df)
    after_bracket_wrappers = int(
        processed["artist_name"].fillna("").astype(str).str.strip().str.startswith("[")
        .mul(processed["artist_name"].fillna("").astype(str).str.strip().str.endswith("]"))
        .sum()
    )
    processed.to_parquet(output_path)
    return {
        "rows": int(len(processed)),
        "artist_name_nulls": int(processed["artist_name"].isna().sum()),
        "artist_name_full_bracket_wrappers_before": before_bracket_wrappers,
        "artist_name_full_bracket_wrappers_after": after_bracket_wrappers,
    }
