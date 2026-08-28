# BizReg system overview

BizReg is a learning-focused digital public-service platform for one government service: **Business Registration**. A citizen creates an account, signs in, chooses the Business Registration service, completes a structured application, and sees the submitted application on their dashboard.

This document describes the system as implemented through Phase 4. The planned capabilities—document uploads, officer review, payments, notifications, certificates, security hardening, tests, and full containerisation—are intentionally not presented as complete.

## Current capabilities

| Area | Implemented behaviour |
| --- | --- |
| Web portal | Next.js App Router interface at `http://localhost:3000` |
| API | FastAPI REST API at `http://localhost:8000/api/v1` |
| Identity | Citizen registration, OAuth2 password-flow login, access/refresh JWTs, `/auth/me` |
| Access control | Backend role dependency with `citizen`, `officer`, and `admin` roles |
| Catalogue | Active services are read from PostgreSQL; Business Registration is seeded |
| Applications | A citizen creates and lists only their own business-registration applications |
| Audit evidence | Creation writes an `application_created` audit event with `submitted` status |
| Schema management | Alembic initial migration creates and seeds the database |

## Planned capabilities

The intended end state includes secure document storage, an explicit workflow engine and officer dashboard, mock payment/notifications, PDF certificates, security controls, automated tests, and frontend/backend Docker images. See [12-demo-script.md](12-demo-script.md) when it is created in Phase 12; do not expect these capabilities in the current build.

## Architecture at a glance

```text
Citizen browser
     |
     |  Next.js pages, local development on :3000
     v
Frontend (frontend/)
     |
     |  HTTPS in production / HTTP locally; JSON REST + Bearer access token
     v
FastAPI (backend/app/), :8000/api/v1
     |
     +-- Authentication and RBAC dependencies
     +-- Route handlers -> service layer -> SQLAlchemy ORM
     |
     v
PostgreSQL :5432                 Redis :6379 (provisioned for later phases)
     |
     +-- users, roles, services, applications, audit records, and future entities
```

The frontend and backend are separate applications. The browser never connects directly to PostgreSQL. Every protected API call supplies `Authorization: Bearer <access-token>`, and the API verifies the token before querying or changing user-owned data.

## Repository map

```text
BizReg/
├── frontend/                    Next.js user interface
│   ├── app/                     App Router pages
│   │   ├── login/               OAuth2 password-flow sign-in page
│   │   ├── register/            Citizen registration page
│   │   ├── dashboard/           Protected citizen dashboard
│   │   └── services/            Catalogue and registration form
│   ├── components/              Reusable client UI components
│   └── lib/auth.ts              Browser token storage and authenticated fetch helper
├── backend/
│   ├── app/
│   │   ├── api/                 Versioned FastAPI routes and dependencies
│   │   ├── core/                Settings and cryptographic helpers
│   │   ├── db/                  SQLAlchemy engine, sessions, and model metadata
│   │   ├── models/              Relational domain models
│   │   ├── schemas/             Request/response validation contracts
│   │   └── services/            Application use-case logic
│   └── alembic/                 Versioned database migrations
├── docs/                        This guide and phase-by-phase study notes
└── docker-compose.yml           Local PostgreSQL and Redis infrastructure
```

## Running the current system

### Prerequisites

- Python 3.11+ (the current environment uses Python 3.13)
- Node.js 18+ and npm
- Docker Desktop, running, for PostgreSQL and Redis

### First-time setup

From the repository root:

```powershell
Copy-Item backend\.env.example backend\.env
docker compose up -d
```

Set a long, private `JWT_SECRET_KEY` in `backend/.env`. The example value is only for local development.

The same file holds the local PostgreSQL credentials used by Docker Compose.
Keep `DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`
consistent; the supplied local values already match.

Start and migrate the API:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

In a separate terminal, start the UI:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. API documentation is available at `http://localhost:8000/docs` and the liveness probe is `http://localhost:8000/api/v1/health`.

## Study order

Read the phase notes in order:

1. [01-scaffolding.md](01-scaffolding.md) — monorepo boundaries and local infrastructure
2. [02-data-modelling.md](02-data-modelling.md) — relational model and migrations
3. [03-auth.md](03-auth.md) — passwords, tokens, and RBAC
4. [04-service-catalogue-and-application.md](04-service-catalogue-and-application.md) — catalogue, validation, and citizen-owned applications

The next best code-reading path is `backend/app/main.py`, then `backend/app/api/v1/router.py`, followed by an individual route and its matching schema/model/service.

For the small shared browser shell and page map, see [frontend-layout.md](frontend-layout.md).
