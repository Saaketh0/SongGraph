# Database Schema Notes (Phase 1A)

## Runtime Database
PostgreSQL (planned as source of truth for app runtime queries).

## PostgreSQL Setup and Run

### Option A: Docker (recommended)
```bash
docker run --name songgraph-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=songgraph \
  -p 5432:5432 \
  -d postgres:16
```

### Option B: Local PostgreSQL
1. Ensure a PostgreSQL 15+ server is running.
2. Create a DB user and DB:
```sql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE songgraph OWNER postgres;
```

### Backend env configuration
Set `DATABASE_URL` in `backend/.env`:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/songgraph
```

### Apply Phase 1 migrations
```bash
cd backend
python3 -m alembic -c alembic.ini upgrade head
```

### Verify migration state
```bash
cd backend
python3 -m alembic -c alembic.ini current
python3 -m alembic -c alembic.ini history
```

### Quick DB verification query
```bash
psql "postgresql://postgres:postgres@localhost:5432/songgraph" \
  -c "\dt" \
  -c "SELECT COUNT(*) FROM songs_stage;" \
  -c "SELECT COUNT(*) FROM song_neighbors_stage;"
```

## Core Tables
- `songs`
  - `song_id` (PK)
  - `song_name`
  - `artist_name`
  - `genre`
- `song_neighbors`
  - `source_song_id`
  - `target_song_id`
  - `neighbor_rank` (1..5)

## Phase 1B Staging Tables
- `songs_stage`
- `song_neighbors_stage`

These are load targets for ingestion validation and are intentionally separate from runtime tables.

## Implemented in Phase 1A
- SQLAlchemy models:
  - `backend/app/db/models/song.py`
  - `backend/app/db/models/song_neighbor.py`
- Alembic migration setup:
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - `backend/alembic/versions/20260409_0001_phase_1a_initial_schema.py`

## Implemented Indexes
- `songs(song_name)`
- `songs(artist_name)`
- `songs(genre)`
- `songs(lower(song_name))`
- `songs(lower(artist_name))`
- `songs(lower(genre))`
- `song_neighbors(source_song_id)`

## Staging Indexes (Phase 1B)
- `songs_stage(song_name)`
- `songs_stage(artist_name)`
- `songs_stage(genre)`
- `song_neighbors_stage(source_song_id)`
