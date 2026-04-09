# Phase 2 Backend

## Implemented Scope
- Search endpoints
- Graph seed endpoints
- Graph expansion endpoint
- Song detail endpoint
- Repository and service layer split

## API Endpoints
- `GET /api/search/songs?q=...`
- `GET /api/search/artists?q=...`
- `GET /api/search/genres?q=...`
- `GET /api/graph/song/{song_id}`
- `GET /api/graph/artist/{artist_name}`
- `GET /api/graph/genre/{genre_name}`
- `POST /api/graph/expand`
- `GET /api/song/{song_id}`

## Notes
- Search ranking: exact match first, prefix match second.
- Expansion enforces graph cap (`GRAPH_NODE_CAP`).
- Data source is controlled by `READ_FROM_STAGE`.
  - `false`: runtime tables
  - `true`: staging tables

## Smoke Test Script
Run automated Phase 2 API smoke checks:

```bash
cd backend
python3 -m app.scripts.smoke_phase2
```

What it does:
- seeds `smoke_*` rows into staging tables
- executes key API calls using FastAPI `TestClient`
- validates status codes and expected payload shapes/counts
- prints JSON summary and exits non-zero on failure
