from __future__ import annotations

import pandas as pd


TEXT_COLUMNS = ["artist", "track_name", "genre"]
NUMERIC_COLUMNS = [
    "danceability",
    "energy",
    "tempo",
    "valence",
    "acousticness",
    "speechiness",
    "instrumentalness",
    "liveness",
    "popularity",
]


def clean_song_dataset(df: pd.DataFrame, max_songs: int | None = None) -> pd.DataFrame:
    required_columns = ["artist", "track_name"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        joined = ", ".join(missing_columns)
        raise ValueError(f"Dataset is missing required columns: {joined}")

    cleaned_df = df.copy()
    cleaned_df = _select_relevant_columns(cleaned_df)
    cleaned_df = _trim_text_columns(cleaned_df)
    cleaned_df = cleaned_df.dropna(subset=required_columns)
    cleaned_df = cleaned_df[
        (cleaned_df["artist"] != "") & (cleaned_df["track_name"] != "")
    ]
    cleaned_df = cleaned_df.drop_duplicates(subset=["artist", "track_name"])

    cleaned_df = _select_song_subset(cleaned_df, max_songs=max_songs)

    return cleaned_df.reset_index(drop=True)


def _select_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    available_columns = [column for column in TEXT_COLUMNS + NUMERIC_COLUMNS if column in df.columns]
    return df[available_columns].copy()


def _trim_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str).str.strip()
            df[column] = df[column].replace({"nan": ""})
    return df


def _select_song_subset(df: pd.DataFrame, max_songs: int | None) -> pd.DataFrame:
    if max_songs is None or len(df) <= max_songs:
        return df

    if "popularity" in df.columns and df["popularity"].notna().any():
        ranked_df = df.sort_values(
            by="popularity",
            ascending=False,
            na_position="last",
        )
        return ranked_df.head(max_songs)

    return df.sample(n=max_songs, random_state=42)
