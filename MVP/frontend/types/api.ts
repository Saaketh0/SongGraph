export type SearchMode = "song" | "artist" | "genre";

export type SongSearchResult = {
  songId: string;
  songName: string;
  artistName: string;
  genre: string;
};

export type ArtistSearchResult = {
  artistName: string;
};

export type GenreSearchResult = {
  genre: string;
};

export type SongSearchResponse = {
  query: string;
  results: SongSearchResult[];
};

export type ArtistSearchResponse = {
  query: string;
  results: ArtistSearchResult[];
};

export type GenreSearchResponse = {
  query: string;
  results: GenreSearchResult[];
};

export type GraphNode = {
  id: string;
  label: string;
  songName: string;
  artist: string;
  genre: string;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  rank: number;
};

export type GraphMeta = {
  seedType: string | null;
  seedValue: string | null;
  visibleNodeCount: number;
  visibleEdgeCount: number;
  reachedLimit: boolean;
};

export type GraphResponse = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  meta: GraphMeta;
};

export type ExpandGraphRequest = {
  visibleNodeIds: string[];
  visibleEdgeIds: string[];
  selectedNodeIds: string[];
  expansionMode: string;
};

export type SimilarSongSummary = {
  songId: string;
  songName: string;
  artistName: string;
  genre: string;
  neighborRank: number;
};

export type SongDetailResponse = {
  songId: string;
  songName: string;
  artistName: string;
  genre: string;
  similarSongs: SimilarSongSummary[];
};

export type HealthResponse = {
  status?: string;
  service?: string;
  environment?: string;
};

