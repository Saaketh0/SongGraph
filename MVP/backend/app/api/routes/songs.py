from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.song import SongDetailResponse
from app.services.songs_service import SongsService


router = APIRouter(prefix="/song", tags=["song"])


@router.get("/{song_id}", response_model=SongDetailResponse)
def get_song_detail(song_id: str, db: Session = Depends(get_db)) -> SongDetailResponse:
    service = SongsService(db)
    try:
        return service.get_song_detail(song_id=song_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

