"use client";

import type { SearchMode } from "../../types/api";

type SearchModeTabsProps = {
  mode: SearchMode;
  onChange: (mode: SearchMode) => void;
};

const MODES: SearchMode[] = ["song", "artist", "genre"];

export function SearchModeTabs({ mode, onChange }: SearchModeTabsProps) {
  return (
    <div className="tabs" role="tablist" aria-label="Search mode">
      {MODES.map((item) => {
        const active = item === mode;
        return (
          <button
            key={item}
            type="button"
            role="tab"
            aria-selected={active}
            className={`tab ${active ? "tab-active" : ""}`}
            onClick={() => onChange(item)}
          >
            {item}
          </button>
        );
      })}
    </div>
  );
}

