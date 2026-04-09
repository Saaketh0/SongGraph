from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.repositories.song_read_repository import SongReadRepositoryMixin
from app.repositories.table_selector import get_song_model, get_song_neighbor_model


class GraphRepository(SongReadRepositoryMixin):
    def __init__(self, db: Session, read_from_stage: bool) -> None:
        self.db = db
        self.song_model = get_song_model(read_from_stage)
        self.neighbor_model = get_song_neighbor_model(read_from_stage)

    def get_songs_by_artist(self, artist_name: str, limit: int) -> list:
        normalized = artist_name.strip().lower()
        stmt = (
            select(self.song_model)
            .where(func.lower(self.song_model.artist_name) == normalized)
            .order_by(self.song_model.song_name.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_songs_by_genre_sample(self, genre_name: str, limit: int) -> list:
        normalized = genre_name.strip().lower()
        stmt = (
            select(self.song_model)
            .where(func.lower(self.song_model.genre) == normalized)
            .order_by(func.random())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_neighbor_edges_for_sources(self, source_song_ids: list[str]) -> list[tuple[str, str, int]]:
        if not source_song_ids:
            return []
        model = self.neighbor_model
        stmt = (
            select(model.source_song_id, model.target_song_id, model.neighbor_rank)
            .where(model.source_song_id.in_(source_song_ids))
            .order_by(model.source_song_id.asc(), model.neighbor_rank.asc())
        )
        rows = self.db.execute(stmt).all()
        return [(row.source_song_id, row.target_song_id, int(row.neighbor_rank)) for row in rows]
