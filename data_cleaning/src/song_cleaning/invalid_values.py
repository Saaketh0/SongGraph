import pandas as pd


BOUNDED_AUDIO_COLUMNS = [
    "valence",
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
]


def get_invalid_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    masks: dict[str, pd.Series] = {}

    for column in BOUNDED_AUDIO_COLUMNS:
        masks[column] = df[column].notna() & ~df[column].between(0, 1)

    masks["tempo"] = df["tempo"].notna() & (df["tempo"] <= 0)
    masks["time_signature"] = df["time_signature"].notna() & (df["time_signature"] <= 0)

    return masks


def collect_invalid_counts(df: pd.DataFrame) -> dict[str, int]:
    masks = get_invalid_masks(df)
    return {column: int(mask.sum()) for column, mask in masks.items()}


def convert_invalid_values_to_null(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy()
    masks = get_invalid_masks(cleaned)
    counts = {column: int(mask.sum()) for column, mask in masks.items()}

    for column, mask in masks.items():
        cleaned.loc[mask, column] = pd.NA

    return cleaned, counts
