# Phase 3 Frontend (Progress)

## Completed: Step 1 (Typed API Client)
- `frontend/lib/api.ts` added with typed functions for:
  - search endpoints
  - graph seed endpoints
  - graph expand endpoint
  - song detail endpoint
  - backend health
- Types are centralized in `frontend/types/api.ts`.

## Completed: Step 2 (Minimal Client State)
- `frontend/store/graphSession.ts` added:
  - search mode/query/results state
  - visible nodes/edges state
  - selected node state
  - reached-limit flag
  - seed/merge/reset actions with dedupe merge logic

## Wiring Status
- `frontend/app/page.tsx` now runs as a client component and uses:
  - typed health call from `lib/api.ts`
  - `useGraphSessionState` from `store/graphSession.ts`

## Completed: Step 3 (Homepage Shell)
- Added modular homepage shell components:
  - `frontend/components/search/SearchModeTabs.tsx`
  - `frontend/components/search/SearchBar.tsx`
  - `frontend/components/search/SearchResults.tsx`
  - `frontend/components/graph/GraphPanel.tsx`
  - `frontend/components/sidebar/SelectedSongPanel.tsx`
- Added responsive shell styling in `frontend/app/globals.css`.

## Completed: Step 4 (Seed Flows)
- Song/artist/genre search is wired to backend.
- Selecting a search result seeds the graph via:
  - `/api/graph/song/{song_id}`
  - `/api/graph/artist/{artist_name}`
  - `/api/graph/genre/{genre_name}`

## Completed: Step 5 (Expand Flow)
- Expand action posts to `/api/graph/expand`.
- Returned nodes/edges are merged with dedupe logic in session state.
- Limit-reached state is surfaced in the graph panel.

## Completed: Step 6 (Song Page)
- Added `/song/[id]` page:
  - `frontend/app/song/[id]/page.tsx`
- Page loads `GET /api/song/{song_id}` and renders metadata + similar songs.
- Added "Open in graph" link back to homepage with `?seedSongId=...`.
