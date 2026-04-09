"use client";

import Link from "next/link";

import type { SongDetailResponse } from "../../types/api";

type SongSummaryCardProps = {
  detail: SongDetailResponse;
};

export function SongSummaryCard({ detail }: SongSummaryCardProps) {
  return (
    <div className="card">
      <p>
        <strong>{detail.songName}</strong>
      </p>
      <p className="muted">
        {detail.artistName} · {detail.genre}
      </p>
      <p>
        <Link className="link" href={`/?seedSongId=${encodeURIComponent(detail.songId)}`}>
          Open in graph
        </Link>
      </p>
      <p>
        <Link className="link" href="/">
          Back to homepage
        </Link>
      </p>
    </div>
  );
}
