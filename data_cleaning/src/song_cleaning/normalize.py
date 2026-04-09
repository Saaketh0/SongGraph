import re

import pandas as pd


WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_text_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
        text = text.replace("'", " ")
        text = text.replace('"', " ")
        text = text.replace(",", " ")

    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    if not text:
        return pd.NA

    return text


def normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for column in ["artist_name", "track_name", "track_id"]:
        normalized[column] = normalized[column].map(clean_text_value)
    return normalized


def build_normalized_artist_track_key(df: pd.DataFrame) -> pd.Series:
    artist = df["artist_name"].astype("string").str.lower().str.strip()
    track = df["track_name"].astype("string").str.lower().str.strip()

    artist = artist.mask(artist == "", pd.NA)
    track = track.mask(track == "", pd.NA)

    key = artist + "||" + track
    missing_mask = artist.isna() | track.isna()
    return key.mask(missing_mask, pd.NA)
