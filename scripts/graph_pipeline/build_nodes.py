from __future__ import annotations

import hashlib
import re
import unicodedata

import pandas as pd


def slugify_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")
    return slug or "unknown"


def add_graph_ids(df: pd.DataFrame) -> pd.DataFrame:
    songs_df = df.copy()
    songs_df["artist_slug"] = _build_collision_safe_slugs(songs_df["artist"])
    songs_df["track_slug"] = _build_collision_safe_slugs(songs_df["track_name"])
    songs_df["artist_id"] = songs_df["artist_slug"].map(lambda slug: f"artist:{slug}")
    songs_df["song_id_base"] = songs_df.apply(
        lambda row: f"song:{row['artist_slug']}:{row['track_slug']}",
        axis=1,
    )
    songs_df["song_id"] = _build_collision_safe_song_ids(songs_df)
    return songs_df


def build_artist_nodes(df: pd.DataFrame) -> list[dict]:
    artist_rows = (
        df[["artist_id", "artist"]]
        .drop_duplicates(subset=["artist_id"])
        .sort_values(by=["artist"])
    )
    return [
        {
            "id": row.artist_id,
            "type": "artist",
            "name": row.artist,
        }
        for row in artist_rows.itertuples(index=False)
    ]


def build_song_nodes(df: pd.DataFrame) -> list[dict]:
    base_columns = ["song_id", "track_name", "artist", "genre", "popularity"]
    feature_columns = [
        column
        for column in df.columns
        if column
        in {
            "danceability",
            "energy",
            "tempo",
            "valence",
            "acousticness",
            "speechiness",
            "instrumentalness",
            "liveness",
        }
    ]

    song_rows = (
        df[base_columns + feature_columns]
        .drop_duplicates(subset=["song_id"])
        .sort_values(by=["artist", "track_name"])
    )

    nodes: list[dict] = []
    for row in song_rows.to_dict(orient="records"):
        node = {
            "id": row["song_id"],
            "type": "song",
            "name": row["track_name"],
            "artist": row["artist"],
            "genre": row.get("genre"),
            "popularity": _to_number(row.get("popularity")),
        }
        for column in feature_columns:
            node[column] = _to_number(row.get(column))
        nodes.append(node)
    return nodes


def _to_number(value: object) -> float | int | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return int(numeric) if numeric.is_integer() else numeric


def _build_collision_safe_slugs(values: pd.Series) -> pd.Series:
    normalized_values = values.fillna("").astype(str).str.strip()
    base_slugs = normalized_values.map(slugify_text)

    slug_counts = normalized_values.groupby(base_slugs).transform("nunique")
    unique_slugs = []
    for original_value, base_slug, needs_suffix in zip(
        normalized_values,
        base_slugs,
        slug_counts > 1,
        strict=False,
    ):
        if needs_suffix:
            unique_slugs.append(f"{base_slug}_{_short_hash(original_value)}")
        else:
            unique_slugs.append(base_slug)
    return pd.Series(unique_slugs, index=values.index)


def _build_collision_safe_song_ids(df: pd.DataFrame) -> pd.Series:
    base_song_ids = df["song_id_base"]
    signatures = (
        df["artist"].fillna("").astype(str).str.strip()
        + "::"
        + df["track_name"].fillna("").astype(str).str.strip()
    )
    song_id_counts = signatures.groupby(base_song_ids).transform("nunique")

    final_song_ids = []
    for base_song_id, signature, needs_suffix in zip(
        base_song_ids,
        signatures,
        song_id_counts > 1,
        strict=False,
    ):
        if needs_suffix:
            final_song_ids.append(f"{base_song_id}_{_short_hash(signature)}")
        else:
            final_song_ids.append(base_song_id)
    return pd.Series(final_song_ids, index=df.index)


def _short_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
