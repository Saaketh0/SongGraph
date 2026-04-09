from __future__ import annotations

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.repositories.table_selector import get_song_model


class SearchRepository:
    def __init__(self, db: Session, read_from_stage: bool) -> None:
        self.db = db
        self.song_model = get_song_model(read_from_stage)

    @staticmethod
    def _normalize_query(query: str) -> str:
        return query.strip().lower()

    @staticmethod
    def _rank_expr(column, normalized: str):
        lowered = func.lower(column)
        return case(
            (lowered == normalized, 0),
            (lowered.like(f"{normalized}%"), 1),
            else_=2,
        )

    @staticmethod
    def _prefix_filter(column, normalized: str):
        lowered = func.lower(column)
        return or_(lowered == normalized, lowered.like(f"{normalized}%"))

    def search_songs(self, query: str, limit: int) -> list[dict[str, str]]:
        normalized = self._normalize_query(query)
        if not normalized:
            return []

        model = self.song_model
        rank_expr = self._rank_expr(model.song_name, normalized)
        stmt = (
            select(model.song_id, model.song_name, model.artist_name, model.genre)
            .where(self._prefix_filter(model.song_name, normalized))
            .order_by(rank_expr, model.song_name.asc(), model.artist_name.asc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "songId": row.song_id,
                "songName": row.song_name,
                "artistName": row.artist_name,
                "genre": row.genre,
            }
            for row in rows
        ]

    def search_artists(self, query: str, limit: int) -> list[dict[str, str]]:
        normalized = self._normalize_query(query)
        if not normalized:
            return []

        model = self.song_model
        rank_expr = self._rank_expr(model.artist_name, normalized)
        stmt = (
            select(
                model.artist_name.label("artist_name"),
                func.min(rank_expr).label("match_rank"),
            )
            .where(self._prefix_filter(model.artist_name, normalized))
            .group_by(model.artist_name)
            .order_by(func.min(rank_expr).asc(), model.artist_name.asc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [{"artistName": row.artist_name} for row in rows]

    def search_genres(self, query: str, limit: int) -> list[dict[str, str]]:
        normalized = self._normalize_query(query)
        if not normalized:
            return []

        model = self.song_model
        rank_expr = self._rank_expr(model.genre, normalized)
        stmt = (
            select(
                model.genre.label("genre"),
                func.min(rank_expr).label("match_rank"),
            )
            .where(self._prefix_filter(model.genre, normalized))
            .group_by(model.genre)
            .order_by(func.min(rank_expr).asc(), model.genre.asc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [{"genre": row.genre} for row in rows]
