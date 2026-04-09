"use client";

import { useEffect, useState } from "react";

import { fetchSongDetail } from "../lib/api";
import type { SongDetailResponse } from "../types/api";

type SongDetailState = {
  detail: SongDetailResponse | null;
  loading: boolean;
  error: string;
};

const initialState: SongDetailState = {
  detail: null,
  loading: false,
  error: "",
};

export function useSongDetail(songId: string | null, reloadToken = 0): SongDetailState {
  const [state, setState] = useState<SongDetailState>(initialState);

  useEffect(() => {
    if (!songId) {
      setState(initialState);
      return;
    }
    const songIdValue = songId;

    let cancelled = false;
    async function loadDetail() {
      setState((previous) => ({
        ...previous,
        loading: true,
        error: "",
      }));
      try {
        const payload = await fetchSongDetail(songIdValue);
        if (!cancelled) {
          setState({
            detail: payload,
            loading: false,
            error: "",
          });
        }
      } catch (error) {
        if (!cancelled) {
          setState({
            detail: null,
            loading: false,
            error: error instanceof Error ? error.message : "Failed to load song detail.",
          });
        }
      }
    }

    loadDetail();
    return () => {
      cancelled = true;
    };
  }, [reloadToken, songId]);

  return state;
}
