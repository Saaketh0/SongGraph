# Quickstart

Minimal steps to run SongGraph locally.

## 1) Start PostgreSQL (Docker)
```bash
docker run --name songgraph-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=songgraph \
  -p 5432:5432 \
  -d postgres:16
```

## 2) Configure env
From repo root:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Default backend DB URL (matches docs):
- `postgresql+psycopg://postgres:postgres@localhost:5432/songgraph`

## 3) Install backend deps
From repo root:
```bash
./.venv/bin/pip install -r backend/requirements.txt
```

## 4) Migrate + load staging data
From repo root:
```bash
cd backend
../.venv/bin/python -m app.scripts.run_phase1 migrate
../.venv/bin/python -m app.scripts.run_phase1 load-stage
```

Optional faster stage load (PostgreSQL COPY):
```bash
cd backend
../.venv/bin/python -m app.scripts.run_phase1 load-stage --ingestion-engine copy
```

Quick API verification without full load:
```bash
cd backend
../.venv/bin/python -m app.scripts.smoke_phase2
```

## 5) Start backend API
From repo root:
```bash
cd backend
READ_FROM_STAGE=true ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend health: `http://127.0.0.1:8000/api/health`

## 6) Start frontend
In another terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://127.0.0.1:3000`

## Docs Index
- Local run guide: `docs/run-localhost.md`
- Phase plan: `PLAN_V1.md`
- API contract: `docs/api-contracts.md`
- DB schema: `docs/database-schema.md`
- Ingestion notes: `docs/ingestion-notes.md`
- Phase docs:
  - `docs/phase-0-setup.md`
  - `docs/phase-1-readme.md`
  - `docs/phase-2-backend.md`
  - `docs/phase-3-frontend.md`
  - `docs/phase-4-cosmograph.md`
  - `docs/phase-5-readme.md`
  - `docs/phase-6-song-detail.md`
