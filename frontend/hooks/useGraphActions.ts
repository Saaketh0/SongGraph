"use client";

import { useCallback, useEffect, useState } from "react";

import {
  expandGraph,
  fetchGraphSeedByArtist,
  fetchGraphSeedByGenre,
  fetchGraphSeedBySong,
  searchArtists,
  searchGenres,
  searchSongs,
} from "../lib/api";
import type {
  ArtistSearchResult,
  GenreSearchResult,
  GraphEdge,
  GraphNode,
  GraphResponse,
  SearchMode,
  SongSearchResult,
} from "../types/api";

type SearchResult = SongSearchResult | ArtistSearchResult | GenreSearchResult;

type GraphSessionActions = {
  setSearchResults: (results: SearchResult[]) => void;
  setGraphSeed: (payload: GraphResponse) => void;
  mergeGraphDelta: (payload: GraphResponse) => void;
};

type UseGraphActionsOptions = {
  mode: SearchMode;
  query: string;
  visibleNodes: GraphNode[];
  visibleEdges: GraphEdge[];
  selectedNodeId: string | null;
  actions: GraphSessionActions;
};

type UseGraphActionsState = {
  searchLoading: boolean;
  graphLoading: boolean;
  searchError: string;
  graphError: string;
  runSearch: () => Promise<void>;
  seedFromResult: (result: SearchResult) => Promise<void>;
  runExpand: () => Promise<void>;
};

export function useGraphActions(options: UseGraphActionsOptions): UseGraphActionsState {
  const { mode, query, visibleNodes, visibleEdges, selectedNodeId, actions } = options;
  const [searchLoading, setSearchLoading] = useState(false);
  const [graphLoading, setGraphLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [graphError, setGraphError] = useState("");

  const seedByMode = useCallback(
    async (seed: SearchResult) => {
      if (mode === "song") {
        return fetchGraphSeedBySong((seed as SongSearchResult).songId);
      }
      if (mode === "artist") {
        return fetchGraphSeedByArtist((seed as ArtistSearchResult).artistName);
      }
      return fetchGraphSeedByGenre((seed as GenreSearchResult).genre);
    },
    [mode],
  );

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const seedSongId = params.get("seedSongId");
    if (!seedSongId) {
      return;
    }
    const seedSongIdValue = seedSongId;
    let cancelled = false;

    async function loadSeedSong() {
      setGraphLoading(true);
      setGraphError("");
      try {
        const payload = await fetchGraphSeedBySong(seedSongIdValue);
        if (!cancelled) {
          actions.setGraphSeed(payload);
        }
      } catch (error) {
        if (!cancelled) {
          setGraphError(error instanceof Error ? error.message : "Failed to load seed song graph.");
        }
      } finally {
        if (!cancelled) {
          setGraphLoading(false);
        }
      }
    }

    loadSeedSong();
    return () => {
      cancelled = true;
    };
  }, [actions]);

  const runSearch = useCallback(async () => {
    const normalized = query.trim();
    if (!normalized) {
      actions.setSearchResults([]);
      return;
    }

    setSearchLoading(true);
    setSearchError("");
    try {
      if (mode === "song") {
        const payload = await searchSongs(normalized);
        actions.setSearchResults(payload.results);
      } else if (mode === "artist") {
        const payload = await searchArtists(normalized);
        actions.setSearchResults(payload.results);
      } else {
        const payload = await searchGenres(normalized);
        actions.setSearchResults(payload.results);
      }
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : "Search failed.");
    } finally {
      setSearchLoading(false);
    }
  }, [actions, mode, query]);

  const seedFromResult = useCallback(
    async (result: SearchResult) => {
      setGraphLoading(true);
      setGraphError("");
      try {
        const payload = await seedByMode(result);
        actions.setGraphSeed(payload);
      } catch (error) {
        setGraphError(error instanceof Error ? error.message : "Failed to seed graph.");
      } finally {
        setGraphLoading(false);
      }
    },
    [actions, seedByMode],
  );

  const runExpand = useCallback(async () => {
    if (!selectedNodeId) {
      return;
    }
    setGraphLoading(true);
    setGraphError("");
    try {
      const payload = await expandGraph({
        visibleNodeIds: visibleNodes.map((node) => node.id),
        visibleEdgeIds: visibleEdges.map((edge) => edge.id),
        selectedNodeIds: [selectedNodeId],
        expansionMode: "selected",
      });
      actions.mergeGraphDelta(payload);
    } catch (error) {
      setGraphError(error instanceof Error ? error.message : "Failed to expand graph.");
    } finally {
      setGraphLoading(false);
    }
  }, [actions, selectedNodeId, visibleEdges, visibleNodes]);

  return {
    searchLoading,
    graphLoading,
    searchError,
    graphError,
    runSearch,
    seedFromResult,
    runExpand,
  };
}
