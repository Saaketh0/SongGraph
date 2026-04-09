"use client";

import { useParams } from "next/navigation";
import { useMemo, useState } from "react";

import { SimilarSongsList } from "../../../components/song/SimilarSongsList";
import { SongSummaryCard } from "../../../components/song/SongSummaryCard";
import { useSongDetail } from "../../../hooks/useSongDetail";

function resolveSongId(rawId: string | string[] | undefined): string | null {
  if (!rawId) {
    return null;
  }
  if (Array.isArray(rawId)) {
    return rawId[0] ?? null;
  }
  return rawId;
}

export default function SongDetailPage() {
  const params = useParams<{ id: string | string[] }>();
  const songId = useMemo(() => resolveSongId(params?.id), [params]);
  const [reloadToken, setReloadToken] = useState(0);
  const { detail, loading, error } = useSongDetail(songId, reloadToken);
  const missingSongId = !songId;

  return (
    <main>
      <h1>Song Detail</h1>
      {missingSongId ? <p className="error">Missing song id.</p> : null}
      {loading ? <p className="muted">Loading...</p> : null}
      {error ? (
        <>
          <p className="error">{error}</p>
          <button type="button" className="button" onClick={() => setReloadToken((value) => value + 1)}>
            Retry
          </button>
        </>
      ) : null}
      {detail ? <SongSummaryCard detail={detail} /> : null}
      {detail ? <h2>Similar Songs</h2> : null}
      {detail ? <SimilarSongsList items={detail.similarSongs} /> : null}
    </main>
  );
}
