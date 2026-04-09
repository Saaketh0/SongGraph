"use client";

import type {
  ArtistSearchResult,
  GenreSearchResult,
  SearchMode,
  SongSearchResult,
} from "../../types/api";

type SearchResultsProps = {
  mode: SearchMode;
  results: (SongSearchResult | ArtistSearchResult | GenreSearchResult)[];
  onSelect: (value: SongSearchResult | ArtistSearchResult | GenreSearchResult) => void;
};

function labelForResult(mode: SearchMode, result: SongSearchResult | ArtistSearchResult | GenreSearchResult): string {
  if (mode === "song") {
    const song = result as SongSearchResult;
    return `${song.songName} · ${song.artistName}`;
  }
  if (mode === "artist") {
    const artist = result as ArtistSearchResult;
    return artist.artistName;
  }
  return (result as GenreSearchResult).genre;
}

function keyForResult(mode: SearchMode, result: SongSearchResult | ArtistSearchResult | GenreSearchResult): string {
  if (mode === "song") {
    return (result as SongSearchResult).songId;
  }
  if (mode === "artist") {
    return `artist:${(result as ArtistSearchResult).artistName}`;
  }
  return `genre:${(result as GenreSearchResult).genre}`;
}

export function SearchResults({ mode, results, onSelect }: SearchResultsProps) {
  if (!results.length) {
    return <p className="muted">No results yet.</p>;
  }

  return (
    <ul className="result-list">
      {results.map((result) => (
        <li key={keyForResult(mode, result)}>
          <button type="button" className="result-item" onClick={() => onSelect(result)}>
            {labelForResult(mode, result)}
          </button>
        </li>
      ))}
    </ul>
  );
}
