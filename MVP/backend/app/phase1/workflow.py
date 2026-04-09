from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from typing import Callable

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.ingestion_copy_service import load_into_stage_tables_via_copy
from app.services.ingestion_service import (
    IngestionStats,
    load_into_stage_tables,
    load_neighbor_edges_from_csv,
    load_song_metadata_from_parquet,
    validate_ingestion_frames,
)


SessionFactory = Callable[[], Session]


@dataclass(slots=True)
class Phase1IngestionOptions:
    parquet_path: Path
    similarity_csv_path: Path
    validate_only: bool = False
    ingestion_engine: Literal["orm", "copy"] = "orm"


def run_phase1b_staging_ingestion(
    options: Phase1IngestionOptions,
    session_factory: SessionFactory = SessionLocal,
) -> dict[str, int | bool | str]:
    songs = load_song_metadata_from_parquet(parquet_path=options.parquet_path)
    neighbors = load_neighbor_edges_from_csv(similarity_csv_path=options.similarity_csv_path)
    validate_ingestion_frames(songs=songs, neighbors=neighbors)

    result: dict[str, int | bool | str] = {
        "validate_only": options.validate_only,
        "ingestion_engine": options.ingestion_engine,
        "songs_in_frame": int(len(songs)),
        "neighbor_edges_in_frame": int(len(neighbors)),
    }
    if options.validate_only:
        return result

    load_fn = load_into_stage_tables if options.ingestion_engine == "orm" else load_into_stage_tables_via_copy
    with session_factory() as session:
        stats: IngestionStats = load_fn(session=session, songs=songs, neighbors=neighbors)
    result.update(
        {
            "songs_loaded_to_stage": stats.songs_loaded,
            "neighbor_edges_loaded_to_stage": stats.neighbor_edges_loaded,
            "unique_neighbor_sources_loaded_to_stage": stats.unique_neighbor_sources,
        }
    )
    return result
