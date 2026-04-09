from __future__ import annotations

from pydantic import BaseModel


class SimilarSongSummary(BaseModel):
    songId: str
    songName: str
    artistName: str
    genre: str
    neighborRank: int


class SongDetailResponse(BaseModel):
    songId: str
    songName: str
    artistName: str
    genre: str
    similarSongs: list[SimilarSongSummary]

