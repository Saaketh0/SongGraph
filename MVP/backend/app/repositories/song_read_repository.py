from __future__ import annotations

from sqlalchemy import select


class SongReadRepositoryMixin:
    song_model: object
    db: object

    def get_song_by_id(self, song_id: str):
        stmt = select(self.song_model).where(self.song_model.song_id == song_id)
        return self.db.scalar(stmt)

    def get_songs_by_ids(self, song_ids: list[str]) -> list:
        if not song_ids:
            return []
        stmt = select(self.song_model).where(self.song_model.song_id.in_(song_ids))
        return list(self.db.scalars(stmt).all())
