import { getApiBaseUrl } from "./config";
import type {
  ArtistSearchResponse,
  ExpandGraphRequest,
  GenreSearchResponse,
  GraphResponse,
  HealthResponse,
  SongDetailResponse,
  SongSearchResponse,
} from "../types/api";

type RequestMethod = "GET" | "POST";

async function requestJson<TResponse>(
  path: string,
  options?: {
    method?: RequestMethod;
    body?: unknown;
    cache?: RequestCache;
  },
): Promise<TResponse> {
  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}${path}`, {
    method: options?.method ?? "GET",
    cache: options?.cache ?? "no-store",
    headers: {
      "Content-Type": "application/json",
    },
    body: options?.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload?.detail) {
        detail = payload.detail;
      }
    } catch {
      // Keep fallback detail.
    }
    throw new Error(detail);
  }
  return (await response.json()) as TResponse;
}

export async function fetchBackendHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/api/health");
}

export async function searchSongs(query: string): Promise<SongSearchResponse> {
  return requestJson<SongSearchResponse>(`/api/search/songs?q=${encodeURIComponent(query)}`);
}

export async function searchArtists(query: string): Promise<ArtistSearchResponse> {
  return requestJson<ArtistSearchResponse>(`/api/search/artists?q=${encodeURIComponent(query)}`);
}

export async function searchGenres(query: string): Promise<GenreSearchResponse> {
  return requestJson<GenreSearchResponse>(`/api/search/genres?q=${encodeURIComponent(query)}`);
}

export async function fetchGraphSeedBySong(songId: string): Promise<GraphResponse> {
  return requestJson<GraphResponse>(`/api/graph/song/${encodeURIComponent(songId)}`);
}

export async function fetchGraphSeedByArtist(artistName: string): Promise<GraphResponse> {
  return requestJson<GraphResponse>(`/api/graph/artist/${encodeURIComponent(artistName)}`);
}

export async function fetchGraphSeedByGenre(genreName: string): Promise<GraphResponse> {
  return requestJson<GraphResponse>(`/api/graph/genre/${encodeURIComponent(genreName)}`);
}

export async function expandGraph(payload: ExpandGraphRequest): Promise<GraphResponse> {
  return requestJson<GraphResponse>("/api/graph/expand", {
    method: "POST",
    body: payload,
  });
}

export async function fetchSongDetail(songId: string): Promise<SongDetailResponse> {
  return requestJson<SongDetailResponse>(`/api/song/${encodeURIComponent(songId)}`);
}

