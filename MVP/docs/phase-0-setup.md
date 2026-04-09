# Phase 0 Setup

## Backend
1. Create a Python virtual environment.
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Copy env template:
   - `cp backend/.env.example backend/.env`
4. Start API:
   - `cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
5. Verify:
   - `GET http://127.0.0.1:8000/api/health`

## Frontend
1. Install dependencies:
   - `cd frontend && npm install`
2. Copy env template:
   - `cp frontend/.env.local.example frontend/.env.local`
3. Start app:
   - `npm run dev`
4. Verify:
   - `GET http://127.0.0.1:3000/api/health`
   - Visit `http://127.0.0.1:3000`

