from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.song_read_repository import SongReadRepositoryMixin
from app.repositories.table_selector import get_song_model, get_song_neighbor_model


class SongRepository(SongReadRepositoryMixin):
    def __init__(self, db: Session, read_from_stage: bool) -> None:
        self.db = db
        self.song_model = get_song_model(read_from_stage)
        self.neighbor_model = get_song_neighbor_model(read_from_stage)

    def get_neighbors_for_song(self, song_id: str) -> list[tuple[str, int]]:
        model = self.neighbor_model
        stmt = (
            select(model.target_song_id, model.neighbor_rank)
            .where(model.source_song_id == song_id)
            .order_by(model.neighbor_rank.asc())
        )
        rows = self.db.execute(stmt).all()
        return [(row.target_song_id, int(row.neighbor_rank)) for row in rows]
