# Phase 1 — Project scaffolding and architecture

## What this phase establishes

BizReg is a monorepo: `frontend` owns the Next.js web experience, `backend` owns the FastAPI REST API, and `docs` contains small phase-specific study notes. This separation makes the browser/client boundary explicit while keeping local development simple.

The frontend uses the Next.js App Router. Its first route, `app/page.tsx`, is deliberately only a landing page; later phases add authentication and application pages as independently understandable routes. Tailwind scans `app` and `components` so styles stay colocated with interface code.

The backend uses versioned routing. `app/main.py` creates the FastAPI application, while `app/api/v1/router.py` collects feature routers below `/api/v1`. This means a route can evolve without exposing unversioned breaking changes. `app/core/config.py` reads settings from the environment (and an untracked local `.env`), keeping secrets and local URLs out of source code.

Docker Compose starts infrastructure only in this phase: PostgreSQL on `localhost:5432` and Redis on `localhost:6379`. The API and web containers are intentionally deferred until Phase 11, after their runtime needs are known.

## Run locally

1. Copy `backend/.env.example` to `backend/.env` and replace `JWT_SECRET_KEY` with a long random value.
2. Start infrastructure from the repository root:

   ```powershell
   docker compose up -d
   ```

3. In one terminal, start the API:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. Visit `http://localhost:8000/api/v1/health` or `http://localhost:8000/docs`.
5. In a second terminal, start the web portal:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

6. Visit `http://localhost:3000`.

## Phase 1 boundaries

Database tables, migrations, authentication, and business-registration functionality do not exist yet. They arrive in later phases so each concept can be introduced and tested in isolation.
