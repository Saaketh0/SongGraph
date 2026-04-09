# Phase 1 README

This document is the consolidated source of truth for Phase 1.

## Scope
- **Phase 1A:** database schema + migrations
- **Phase 1B:** source ingestion into dedicated staging tables
- **Phase 1C (next):** post-load audits and promotion strategy

## Key Decisions
- Runtime tables: `songs`, `song_neighbors`
- Staging tables (Phase 1B load target): `songs_stage`, `song_neighbors_stage`
- Source metadata comes from `final_song_data.parquet`
- Source neighbors come from `song_similarities.csv` (`sim_song_1..sim_song_5`)
- Source `track_id` maps to runtime/staging `song_id`

## Why this differs from original plan
- Local Parquet files do not contain neighbor columns.
- Neighbor links are loaded from the separate similarity CSV and validated against metadata song IDs.

## Consolidated Code Paths
- Models:
  - `backend/app/db/models/song.py`
  - `backend/app/db/models/song_neighbor.py`
  - `backend/app/db/models/staging_song.py`
  - `backend/app/db/models/staging_song_neighbor.py`
- Migrations:
  - `backend/alembic/versions/20260409_0001_phase_1a_initial_schema.py`
  - `backend/alembic/versions/20260409_0002_phase_1b_stage_tables.py`
- Workflow:
  - `backend/app/phase1/workflow.py`
- Scripts:
  - `backend/app/scripts/run_phase1.py` (canonical)
  - `backend/app/scripts/load_stage_tables.py` (deprecated compatibility wrapper)

## Validation Rules
- Song IDs must be non-empty and unique.
- Exactly 5 neighbor ranks per source song.
- Source and target neighbor IDs must exist in songs metadata.
- No self-loop edges.
- Neighbor rank is constrained to `1..5`.

## How To Run

### 1) Apply migrations (Phase 1A)
```bash
cd backend
python3 -m app.scripts.run_phase1 migrate
```

### 2) Validate source files only (Phase 1B dry run)
```bash
cd backend
python3 -m app.scripts.run_phase1 validate
```

### 3) Load stage tables (Phase 1B write path)
```bash
cd backend
python3 -m app.scripts.run_phase1 load-stage
```

### 3b) Load with PostgreSQL COPY (isolated optional engine)
```bash
cd backend
python3 -m app.scripts.run_phase1 load-stage --ingestion-engine copy
```

### 4) Run both migration + stage load
```bash
cd backend
python3 -m app.scripts.run_phase1 all
```

## Optional Path Overrides
```bash
cd backend
python3 -m app.scripts.run_phase1 validate \
  --parquet-path /abs/path/final_song_data.parquet \
  --similarity-csv-path /abs/path/song_similarities.csv
```

Engine override is available for both `validate` and `load-stage`:
```bash
python3 -m app.scripts.run_phase1 load-stage --ingestion-engine orm
python3 -m app.scripts.run_phase1 load-stage --ingestion-engine copy
```
