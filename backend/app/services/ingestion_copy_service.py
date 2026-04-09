from __future__ import annotations

from io import StringIO

import pandas as pd
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.models.staging_song_neighbor import StagingSongNeighbor
from app.services.ingestion_service import IngestionStats


def _copy_frame_to_table(
    session: Session,
    frame: pd.DataFrame,
    table_name: str,
    columns: list[str],
) -> int:
    if frame.empty:
        return 0

    ordered = frame[columns]
    buffer = StringIO()
    ordered.to_csv(buffer, index=False, header=False, na_rep="")
    buffer.seek(0)

    copy_sql = (
        f"COPY {table_name} ({', '.join(columns)}) "
        "FROM STDIN WITH (FORMAT CSV, DELIMITER ',', QUOTE '\"', ESCAPE '\"', NULL '')"
    )
    connection = session.connection()
    dbapi_connection = connection.connection
    with dbapi_connection.cursor() as cursor:
        with cursor.copy(copy_sql) as copy:
            copy.write(buffer.read())
    return int(len(ordered))


def load_into_stage_tables_via_copy(
    session: Session,
    songs: pd.DataFrame,
    neighbors: pd.DataFrame,
) -> IngestionStats:
    session.execute(text("DELETE FROM song_neighbors_stage"))
    session.execute(text("DELETE FROM songs_stage"))

    songs_loaded = _copy_frame_to_table(
        session=session,
        frame=songs,
        table_name="songs_stage",
        columns=["song_id", "song_name", "artist_name", "genre"],
    )
    neighbor_edges_loaded = _copy_frame_to_table(
        session=session,
        frame=neighbors,
        table_name="song_neighbors_stage",
        columns=["source_song_id", "target_song_id", "neighbor_rank"],
    )
    session.commit()

    unique_sources = session.scalar(select(func.count(func.distinct(StagingSongNeighbor.source_song_id)))) or 0
    return IngestionStats(
        songs_loaded=songs_loaded,
        neighbor_edges_loaded=neighbor_edges_loaded,
        unique_neighbor_sources=int(unique_sources),
    )
