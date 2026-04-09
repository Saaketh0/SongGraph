from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Song(Base):
    __tablename__ = "songs"

    song_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    song_name: Mapped[str] = mapped_column(String(512), nullable=False)
    artist_name: Mapped[str] = mapped_column(String(512), nullable=False)
    genre: Mapped[str] = mapped_column(String(256), nullable=False)

    neighbors_out: Mapped[list["SongNeighbor"]] = relationship(
        back_populates="source_song",
        cascade="all, delete-orphan",
        foreign_keys="SongNeighbor.source_song_id",
    )
    neighbors_in: Mapped[list["SongNeighbor"]] = relationship(
        back_populates="target_song",
        foreign_keys="SongNeighbor.target_song_id",
    )

