"use client";

import Link from "next/link";

import type { SimilarSongSummary } from "../../types/api";

const DEFAULT_NEIGHBOR_LIMIT = 5;

type SimilarSongsListProps = {
  items: SimilarSongSummary[];
  limit?: number;
};

export function SimilarSongsList({ items, limit = DEFAULT_NEIGHBOR_LIMIT }: SimilarSongsListProps) {
  if (items.length === 0) {
    return <p className="muted">No similar songs were returned for this song.</p>;
  }

  return (
    <ul className="mini-list">
      {items.slice(0, limit).map((item) => (
        <li key={item.songId}>
          {item.neighborRank}.{" "}
          <Link className="link" href={`/song/${encodeURIComponent(item.songId)}`}>
            {item.songName}
          </Link>{" "}
          ({item.artistName}) ·{" "}
          <Link className="link" href={`/?seedSongId=${encodeURIComponent(item.songId)}`}>
            Open in graph
          </Link>
        </li>
      ))}
    </ul>
  );
}
