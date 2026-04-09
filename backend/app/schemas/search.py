from __future__ import annotations

from pydantic import BaseModel


class SongSearchResult(BaseModel):
    songId: str
    songName: str
    artistName: str
    genre: str


class ArtistSearchResult(BaseModel):
    artistName: str


class GenreSearchResult(BaseModel):
    genre: str


class SongSearchResponse(BaseModel):
    query: str
    results: list[SongSearchResult]


class ArtistSearchResponse(BaseModel):
    query: str
    results: list[ArtistSearchResult]


class GenreSearchResponse(BaseModel):
    query: str
    results: list[GenreSearchResult]

