"use client";

import Link from "next/link";

import type { GraphNode, SongDetailResponse } from "../../types/api";

type SelectedSongPanelProps = {
  selectedNode: GraphNode | null;
  detail: SongDetailResponse | null;
  loading: boolean;
  error: string;
};

export function SelectedSongPanel({ selectedNode, detail, loading, error }: SelectedSongPanelProps) {
  return (
    <section className="panel">
      <h2>Selected Song</h2>
      {!selectedNode ? <p className="muted">Select a song node to inspect details.</p> : null}
      {selectedNode ? (
        <>
          <p>
            <strong>{selectedNode.songName}</strong>
          </p>
          <p className="muted">
            {selectedNode.artist} · {selectedNode.genre}
          </p>
          <p>
            <Link className="link" href={`/song/${encodeURIComponent(selectedNode.id)}`}>
              Open song page
            </Link>
          </p>
        </>
      ) : null}

      {loading ? <p className="muted">Loading detail...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      {detail ? (
        <>
          <p className="muted">Similar songs: {detail.similarSongs.length}</p>
          <ul className="mini-list">
            {detail.similarSongs.slice(0, 5).map((item) => (
              <li key={item.songId}>
                {item.neighborRank}. {item.songName}
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  );
}

