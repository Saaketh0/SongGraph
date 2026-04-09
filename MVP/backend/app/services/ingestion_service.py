from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from app.db.models.staging_song import StagingSong
from app.db.models.staging_song_neighbor import StagingSongNeighbor

SONG_COLUMNS = ["track_id", "track_name", "artist_name", "genre"]
NEIGHBOR_COLUMNS = ["track_id", "sim_song_1", "sim_song_2", "sim_song_3", "sim_song_4", "sim_song_5"]
DEFAULT_INSERT_BATCH_SIZE = 5_000


@dataclass(slots=True)
class IngestionStats:
    songs_loaded: int
    neighbor_edges_loaded: int
    unique_neighbor_sources: int


def _normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _clip_column(df: pd.DataFrame, column: str, max_length: int) -> None:
    df[column] = df[column].str.slice(0, max_length)


def load_song_metadata_from_parquet(parquet_path: Path) -> pd.DataFrame:
    songs = pd.read_parquet(parquet_path, columns=SONG_COLUMNS)
    songs = songs.rename(columns={"track_id": "song_id", "track_name": "song_name"})
    songs = songs.astype({"song_id": "string", "song_name": "string", "artist_name": "string", "genre": "string"})
    songs = songs.map(_normalize_text)
    _clip_column(songs, "song_id", 128)
    _clip_column(songs, "song_name", 512)
    _clip_column(songs, "artist_name", 512)
    _clip_column(songs, "genre", 256)
    songs.loc[songs["artist_name"] == "", "artist_name"] = "Unknown"
    songs.loc[songs["genre"] == "", "genre"] = "Unknown"
    songs = songs[(songs["song_id"] != "") & (songs["song_name"] != "")]
    songs = songs.drop_duplicates(subset=["song_id"], keep="first")
    return songs.reset_index(drop=True)


def load_neighbor_edges_from_csv(similarity_csv_path: Path) -> pd.DataFrame:
    source = pd.read_csv(similarity_csv_path, usecols=NEIGHBOR_COLUMNS, dtype="string")
    source = source.map(_normalize_text)
    _clip_column(source, "track_id", 128)
    for rank in range(1, 6):
        _clip_column(source, f"sim_song_{rank}", 128)
    source = source[source["track_id"] != ""].copy()

    edges: list[pd.DataFrame] = []
    for rank in range(1, 6):
        column_name = f"sim_song_{rank}"
        frame = source[["track_id", column_name]].rename(
            columns={"track_id": "source_song_id", column_name: "target_song_id"}
        )
        frame["neighbor_rank"] = rank
        edges.append(frame)

    neighbors = pd.concat(edges, ignore_index=True)
    neighbors = neighbors[(neighbors["source_song_id"] != "") & (neighbors["target_song_id"] != "")]
    return neighbors.reset_index(drop=True)


def validate_ingestion_frames(songs: pd.DataFrame, neighbors: pd.DataFrame) -> None:
    duplicate_song_ids = songs["song_id"].duplicated().sum()
    if duplicate_song_ids:
        raise ValueError(f"Duplicate song_id values found in songs frame: {duplicate_song_ids}")

    source_counts = neighbors.groupby("source_song_id")["neighbor_rank"].nunique()
    if not source_counts.empty and (source_counts != 5).any():
        invalid_sources = int((source_counts != 5).sum())
        raise ValueError(f"Neighbor ranks are incomplete for {invalid_sources} source songs.")

    song_id_set = set(songs["song_id"].tolist())
    missing_sources = neighbors.loc[~neighbors["source_song_id"].isin(song_id_set), "source_song_id"].nunique()
    if missing_sources:
        raise ValueError(f"Found {missing_sources} source song IDs missing from songs metadata.")

    missing_targets = neighbors.loc[~neighbors["target_song_id"].isin(song_id_set), "target_song_id"].nunique()
    if missing_targets:
        raise ValueError(f"Found {missing_targets} target song IDs missing from songs metadata.")

    self_loops = (neighbors["source_song_id"] == neighbors["target_song_id"]).sum()
    if self_loops:
        raise ValueError(f"Found {int(self_loops)} self-loop neighbor edges.")


def _iter_records(frame: pd.DataFrame):
    columns = list(frame.columns)
    for row in frame.itertuples(index=False, name=None):
        yield dict(zip(columns, row, strict=False))


def _insert_in_batches(
    session: Session,
    model,
    frame: pd.DataFrame,
    batch_size: int = DEFAULT_INSERT_BATCH_SIZE,
) -> int:
    batch: list[dict[str, object]] = []
    inserted = 0
    for record in _iter_records(frame):
        batch.append(record)
        if len(batch) >= batch_size:
            session.execute(insert(model), batch)
            inserted += len(batch)
            batch = []
    if batch:
        session.execute(insert(model), batch)
        inserted += len(batch)
    return inserted


def load_into_stage_tables(session: Session, songs: pd.DataFrame, neighbors: pd.DataFrame) -> IngestionStats:
    session.execute(delete(StagingSongNeighbor))
    session.execute(delete(StagingSong))

    songs_loaded = _insert_in_batches(session, StagingSong, songs) if not songs.empty else 0
    neighbor_edges_loaded = (
        _insert_in_batches(session, StagingSongNeighbor, neighbors) if not neighbors.empty else 0
    )
    session.commit()

    unique_sources = session.scalar(select(func.count(func.distinct(StagingSongNeighbor.source_song_id)))) or 0
    return IngestionStats(
        songs_loaded=songs_loaded,
        neighbor_edges_loaded=neighbor_edges_loaded,
        unique_neighbor_sources=int(unique_sources),
    )
