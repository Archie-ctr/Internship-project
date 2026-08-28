# BizReg

BizReg is a learning-focused, Irembo-style digital public-service platform for business registration.

Start with the [system overview](docs/00-system-overview.md), then read the [architecture guide](docs/architecture.md) and [implemented API reference](docs/api-reference.md). The repository is intentionally organised by delivery phase, with a study note for each completed phase.

## Repository layout

- `frontend/` — Next.js citizen and officer web portal.
- `backend/` — FastAPI REST API and domain logic.
- `docs/` — short study notes for each build phase.

Later phases add the database models, authentication, business-registration workflow, documents, payments, and tests.

## Current local start command

See the full setup instructions in [docs/00-system-overview.md](docs/00-system-overview.md). In short, start Docker infrastructure, run Alembic migrations, start FastAPI from `backend/`, then run Next.js from `frontend/`.
