from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.graph import ExpandGraphRequest, GraphResponse
from app.services.graph_service import GraphService


router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/song/{song_id}", response_model=GraphResponse)
def graph_seed_song(song_id: str, db: Session = Depends(get_db)) -> GraphResponse:
    service = GraphService(db)
    try:
        return service.seed_from_song(song_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/artist/{artist_name:path}", response_model=GraphResponse)
def graph_seed_artist(artist_name: str, db: Session = Depends(get_db)) -> GraphResponse:
    service = GraphService(db)
    try:
        return service.seed_from_artist(artist_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/genre/{genre_name}", response_model=GraphResponse)
def graph_seed_genre(genre_name: str, db: Session = Depends(get_db)) -> GraphResponse:
    service = GraphService(db)
    return service.seed_from_genre(genre_name)


@router.post("/expand", response_model=GraphResponse)
def graph_expand(payload: ExpandGraphRequest, db: Session = Depends(get_db)) -> GraphResponse:
    service = GraphService(db)
    return service.expand_graph(payload)
