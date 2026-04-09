from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SongNeighbor(Base):
    __tablename__ = "song_neighbors"
    __table_args__ = (
        PrimaryKeyConstraint("source_song_id", "neighbor_rank", name="pk_song_neighbors"),
        UniqueConstraint("source_song_id", "target_song_id", name="uq_song_neighbors_source_target"),
        CheckConstraint("neighbor_rank BETWEEN 1 AND 5", name="ck_song_neighbors_rank_range"),
        CheckConstraint("source_song_id <> target_song_id", name="ck_song_neighbors_not_self"),
    )

    source_song_id: Mapped[str] = mapped_column(
        ForeignKey("songs.song_id", ondelete="CASCADE"),
        nullable=False,
    )
    target_song_id: Mapped[str] = mapped_column(
        ForeignKey("songs.song_id", ondelete="RESTRICT"),
        nullable=False,
    )
    neighbor_rank: Mapped[int] = mapped_column(Integer, nullable=False)

    source_song: Mapped["Song"] = relationship(
        back_populates="neighbors_out",
        foreign_keys=[source_song_id],
    )
    target_song: Mapped["Song"] = relationship(
        back_populates="neighbors_in",
        foreign_keys=[target_song_id],
    )

