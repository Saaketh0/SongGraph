# Phase 6 Song Detail (Progress)

## Goal
Complete `/song/[id]` detail routing and keep the page aligned with the MVP contract.

## Implemented
- Song detail page uses shared hook logic:
  - `frontend/hooks/useSongDetail.ts`
- Song detail UI is modularized into focused components:
  - `frontend/components/song/SongSummaryCard.tsx`
  - `frontend/components/song/SimilarSongsList.tsx`
- Similar songs list is constrained to top 5 neighbors on the page.
- Song page includes:
  - metadata display
  - retry action on request failure
  - "Open in graph" action
  - links to related song detail pages

## Notes
- Homepage selected-song sidebar and song detail page now share the same song-detail fetch hook.
- This phase is ready to transition into Phase 7 polish tasks (search UX, graph styling, limit messaging, empty states).
