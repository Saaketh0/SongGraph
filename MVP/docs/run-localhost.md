# Run SongGraph On Localhost

This guide starts the full app locally:
- PostgreSQL
- FastAPI backend
- Next.js frontend

## 1) Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ (or Docker)

## 2) Environment files
From repo root:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Ensure these values:

```env
# backend/.env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/songgraph
READ_FROM_STAGE=true

# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## 3) Start PostgreSQL

### Option A: Docker
```bash
docker run --name songgraph-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=songgraph \
  -p 5432:5432 \
  -d postgres:16
```

### Option B: Local service
Create DB/user if needed:
```sql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE songgraph OWNER postgres;
```

## 4) Install backend dependencies
From repo root:

```bash
./.venv/bin/pip install -r backend/requirements.txt
```

## 5) Apply migrations and load staging data
From repo root:

```bash
cd backend
../.venv/bin/python -m app.scripts.run_phase1 migrate
../.venv/bin/python -m app.scripts.run_phase1 load-stage
```

Notes:
- `load-stage` can take time on full dataset.
- Optional: use PostgreSQL COPY for faster loading:
  ```bash
  cd backend
  ../.venv/bin/python -m app.scripts.run_phase1 load-stage --ingestion-engine copy
  ```
- For quick API checks only, run `../.venv/bin/python -m app.scripts.smoke_phase2` instead (it seeds a tiny fixture).

## 6) Start backend API
From repo root:

```bash
cd backend
READ_FROM_STAGE=true ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL: `http://127.0.0.1:8000`

## 7) Install frontend dependencies
In another terminal:

```bash
cd frontend
npm install
```

## 8) Start frontend
In another terminal:

```bash
cd frontend
npm run dev
```

Frontend URL: `http://127.0.0.1:3000`

## 9) Quick verification
- Backend health: `http://127.0.0.1:8000/api/health`
- Main app: `http://127.0.0.1:3000`
