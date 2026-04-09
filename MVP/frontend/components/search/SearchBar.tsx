"use client";

type SearchBarProps = {
  query: string;
  loading: boolean;
  onQueryChange: (value: string) => void;
  onSearch: () => void;
};

export function SearchBar({ query, loading, onQueryChange, onSearch }: SearchBarProps) {
  return (
    <div className="search-row">
      <input
        className="input"
        value={query}
        placeholder="Type to search..."
        onChange={(event) => onQueryChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onSearch();
          }
        }}
      />
      <button type="button" className="button" onClick={onSearch} disabled={loading}>
        {loading ? "Searching..." : "Search"}
      </button>
    </div>
  );
}

