import pandas as pd

from .columns import ARTIST_TRACK_FILL_COLUMNS, TRACK_ID_FILL_COLUMNS
from .normalize import build_normalized_artist_track_key


def build_unique_fill_lookup(df: pd.DataFrame, group_column: str, target_column: str) -> pd.DataFrame:
    non_null = df.loc[df[target_column].notna(), [group_column, target_column]].drop_duplicates()
    grouped = (
        non_null.groupby(group_column, dropna=False)[target_column]
        .agg(["nunique", "first"])
        .rename(columns={"nunique": "unique_count", "first": "fill_value"})
        .reset_index()
    )
    return grouped


def fill_column_from_group(df: pd.DataFrame, group_column: str, target_column: str) -> tuple[pd.DataFrame, int]:
    lookup = build_unique_fill_lookup(df, group_column, target_column).set_index(group_column)
    unique_count = df[group_column].map(lookup["unique_count"])
    fill_value = df[group_column].map(lookup["fill_value"])

    fill_mask = df[target_column].isna().to_numpy() & unique_count.eq(1).to_numpy()
    fill_count = int(fill_mask.sum())
    df.loc[fill_mask, target_column] = fill_value[fill_mask].to_numpy()

    return df, fill_count


def fill_columns_from_group(
    df: pd.DataFrame,
    group_column: str,
    target_columns: list[str],
) -> tuple[pd.DataFrame, dict[str, int]]:
    counts: dict[str, int] = {}

    for target_column in target_columns:
        df, counts[target_column] = fill_column_from_group(df, group_column, target_column)

    return df, counts


def fill_from_track_id(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    eligible = df.loc[df["track_id"].notna()].copy()
    ineligible = df.loc[df["track_id"].isna()].copy()
    filled_eligible, counts = fill_columns_from_group(eligible, "track_id", TRACK_ID_FILL_COLUMNS)
    combined = pd.concat([filled_eligible, ineligible], axis=0).sort_index()
    return combined, counts


def fill_from_artist_track(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    filled = df.copy()
    filled["artist_track_key"] = build_normalized_artist_track_key(filled)

    eligible = filled.loc[filled["artist_track_key"].notna()].copy()
    ineligible = filled.loc[filled["artist_track_key"].isna()].copy()

    filled_eligible, counts = fill_columns_from_group(
        eligible,
        "artist_track_key",
        ARTIST_TRACK_FILL_COLUMNS,
    )

    combined = pd.concat([filled_eligible, ineligible], axis=0).sort_index()
    combined = combined.drop(columns=["artist_track_key"])
    return combined, counts


def run_deterministic_fill(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, int]]]:
    after_track_id, track_id_counts = fill_from_track_id(df)
    after_artist_track, artist_track_counts = fill_from_artist_track(after_track_id)

    return after_artist_track, {
        "track_id_fill_counts": track_id_counts,
        "artist_track_fill_counts": artist_track_counts,
    }
