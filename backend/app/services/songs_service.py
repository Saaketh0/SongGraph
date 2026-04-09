from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.song_repository import SongRepository
from app.schemas.song import SimilarSongSummary, SongDetailResponse


class SongsService:
    def __init__(self, db: Session) -> None:
        settings = get_settings()
        self.repository = SongRepository(db=db, read_from_stage=settings.read_from_stage)

    def get_song_detail(self, song_id: str) -> SongDetailResponse:
        song = self.repository.get_song_by_id(song_id)
        if song is None:
            raise ValueError(f"Song not found: {song_id}")

        neighbor_rows = self.repository.get_neighbors_for_song(song_id)
        neighbor_ids = [target_id for target_id, _ in neighbor_rows]
        neighbors = self.repository.get_songs_by_ids(neighbor_ids)
        neighbor_lookup = {neighbor.song_id: neighbor for neighbor in neighbors}

        similar_songs: list[SimilarSongSummary] = []
        for target_id, rank in neighbor_rows:
            neighbor_song = neighbor_lookup.get(target_id)
            if not neighbor_song:
                continue
            similar_songs.append(
                SimilarSongSummary(
                    songId=neighbor_song.song_id,
                    songName=neighbor_song.song_name,
                    artistName=neighbor_song.artist_name,
                    genre=neighbor_song.genre,
                    neighborRank=rank,
                )
            )

        return SongDetailResponse(
            songId=song.song_id,
            songName=song.song_name,
            artistName=song.artist_name,
            genre=song.genre,
            similarSongs=similar_songs,
        )

