from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import (
    ArtistSearchResponse,
    GenreSearchResponse,
    SongSearchResponse,
)
from app.services.search_service import SearchService


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/songs", response_model=SongSearchResponse)
def search_songs(q: str = Query(default=""), db: Session = Depends(get_db)) -> SongSearchResponse:
    service = SearchService(db)
    return SongSearchResponse(query=q, results=service.search_songs(query=q))


@router.get("/artists", response_model=ArtistSearchResponse)
def search_artists(q: str = Query(default=""), db: Session = Depends(get_db)) -> ArtistSearchResponse:
    service = SearchService(db)
    return ArtistSearchResponse(query=q, results=service.search_artists(query=q))


@router.get("/genres", response_model=GenreSearchResponse)
def search_genres(q: str = Query(default=""), db: Session = Depends(get_db)) -> GenreSearchResponse:
    service = SearchService(db)
    return GenreSearchResponse(query=q, results=service.search_genres(query=q))

