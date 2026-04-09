# Ingestion Notes (Phase 1B)

## Source
Parquet dataset with song identity fields and five ranked neighbor IDs.

## Target
Phase 1B loads into dedicated staging tables:
- `songs_stage`
- `song_neighbors_stage`

Runtime tables (`songs`, `song_neighbors`) remain untouched during this phase.

## Validation Rules
- Song ID exists and is unique
- Exactly five neighbors per song
- Neighbor rank maps to 1..5
- Artist and genre are present
- Source and target neighbor IDs exist in staged songs
- Self-loop neighbor edges are rejected

## Implemented Phase 1B Components
- Service: `backend/app/services/ingestion_service.py`
- Optional isolated COPY service: `backend/app/services/ingestion_copy_service.py`
- Workflow: `backend/app/phase1/workflow.py`
- Canonical script: `backend/app/scripts/run_phase1.py`
- Deprecated compatibility wrapper: `backend/app/scripts/load_stage_tables.py`
- Migration: `backend/alembic/versions/20260409_0002_phase_1b_stage_tables.py`

## Engine Selection
- Default: `--ingestion-engine orm`
- Optional: `--ingestion-engine copy`
- The COPY implementation is isolated and opt-in; the rest of the app continues to use existing repositories/services unchanged.
