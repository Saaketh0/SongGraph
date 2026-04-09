from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.search_repository import SearchRepository


class SearchService:
    def __init__(self, db: Session) -> None:
        settings = get_settings()
        self.result_limit = settings.search_result_limit
        self.repository = SearchRepository(db=db, read_from_stage=settings.read_from_stage)

    def search_songs(self, query: str) -> list[dict[str, str]]:
        return self.repository.search_songs(query=query, limit=self.result_limit)

    def search_artists(self, query: str) -> list[dict[str, str]]:
        return self.repository.search_artists(query=query, limit=self.result_limit)

    def search_genres(self, query: str) -> list[dict[str, str]]:
        return self.repository.search_genres(query=query, limit=self.result_limit)

