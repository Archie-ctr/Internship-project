# 14-Day Practical Curriculum: BizReg Platform Development

**Project**: Digital Public-Service Platform for Business Registration  
**Framework**: FastAPI + Next.js + PostgreSQL + Redis  
**Curriculum by**: Dr. Ntivuguruzwa Jean Ali — SecureAI Labs  
**Reference**: [Irembo](https://www.irembo.gov.rw/)

---

## Curriculum Overview

| Day | Topic | Status |
|-----|-------|--------|
| 1 | Problem, Requirements & Architecture | ✅ Complete |
| 2 | UI/UX & Frontend Foundations | ✅ Complete |
| 3 | Backend & REST APIs | ✅ Complete |
| 4 | PostgreSQL & Data Modelling | ✅ Complete |
| 5 | Authentication & Authorization | ✅ Complete |
| 6 | Application Forms & Documents | ✅ Complete |
| 7 | Workflow Engine | ✅ Complete |
| 8 | Payments & Notifications | ✅ Complete |
| 9 | API Integration & Interoperability | 🔄 In Progress |
| 10 | Security by Design | 🔄 In Progress |
| 11 | Testing & Quality | 🔄 In Progress |
| 12 | Deployment & DevOps | 🔄 In Progress |
| 13 | AI & Intelligent Services | ⏳ Planned |
| 14 | Capstone, Demo & Future Architecture | ⏳ Planned |

---

## DAY 1 — Problem, Requirements & Architecture ✅

**Objectives**
1. Understand digital public-service platforms
2. Select Business Registration as the MVP service
3. Map citizen-to-government workflow
4. Define functional and non-functional requirements
5. Design system architecture and data flow
6. Set up Git/GitHub and development environments

**Deliverables**
- `docs/DAY-1-ANALYSIS.md` — comprehensive requirements analysis
- `docs/ARCHITECTURE-DIAGRAMS.md` — 12 Mermaid architecture diagrams
- `docs/architecture.md` — system overview
- GitHub repository + 5 CI/CD workflow files configured

---

## DAY 2 — UI/UX & Frontend Foundations ✅

**Objectives**
1. React/Next.js project setup with TypeScript + Tailwind CSS
2. Component architecture and layouts
3. App Router routing structure
4. Responsive design patterns
5. Landing page, service catalogue and navigation

**What was built**
- `frontend/` — Next.js 14 App Router project
- `frontend/app/layout.tsx` — root layout with `SiteHeader` + footer
- `frontend/app/page.tsx` — marketing landing page
- `frontend/components/SiteHeader.tsx` — auth-aware navigation header
- `frontend/components/ProtectedRoute.tsx` — client-side auth guard
- Tailwind CSS configured with responsive breakpoints

---

## DAY 3 — Backend & REST APIs ✅

**Objectives**
1. FastAPI project structure
2. REST principles and URL design
3. Pydantic request/response models
4. Validation and error handling
5. Service catalogue and application APIs

**What was built**
- `backend/app/main.py` — app factory with CORS, rate limiting middleware
- `backend/app/api/v1/router.py` — single composition point for all routes
- `backend/app/api/v1/routes/health.py` — `GET /health`
- `backend/app/api/v1/routes/services.py` — `GET /services`
- `backend/app/api/v1/routes/applications.py` — citizen application endpoints
- `backend/app/api/v1/routes/officer.py` — officer/admin workflow endpoints
- `backend/app/api/v1/routes/documents.py` — file upload/download
- `backend/app/api/v1/routes/payments.py` — mock payment flow
- `backend/app/api/v1/routes/notifications.py` — notification history + dispatch

---

## DAY 4 — PostgreSQL & Data Modelling ✅

**Objectives**
1. Design all entities with relationships and constraints
2. SQLAlchemy ORM models with typed `Mapped` columns
3. Alembic migrations
4. CRUD operations and service layer
5. Connect FastAPI to PostgreSQL

**Database schema** (`alembic/versions/20260827_0001_initial_schema.py`)
- `roles` — 3 seeded: citizen, officer, admin
- `users` — UUID PK, bcrypt password hash, FK→roles
- `services` — service catalogue, seeded with business-registration
- `application_statuses` — 8 seeded workflow states
- `applications` — UUID PK, FK→users/services/statuses, JSON form_data
- `documents` — file metadata, storage_key for disk/S3
- `payments` — one-to-one with application, Numeric(12,2) amount
- `notifications` — email/SMS delivery records
- `workflow_tasks` — officer review assignments
- `audit_logs` — append-only event history

---

## DAY 5 — Authentication & Authorization ✅

**Objectives**
1. Registration and login
2. bcrypt password hashing
3. JWT access + refresh tokens (HS256)
4. Roles: citizen, officer, administrator
5. RBAC via `require_role` dependency factory
6. Protected endpoints

**What was built**
- `backend/app/core/security.py` — `hash_password`, `verify_password`, `create_access_token`, `create_refresh_token`, `decode_token`
- `backend/app/api/deps.py` — `get_current_user`, `require_role(*roles)`
- `backend/app/api/v1/routes/auth.py`:
  - `POST /auth/register` — creates citizen account, returns JWT pair
  - `POST /auth/token` — OAuth2 password flow
  - `POST /auth/refresh` — stateless token refresh
  - `GET /auth/me` — returns current user identity
- `frontend/lib/auth.ts` — token storage, `apiFetch`, `clearTokens`
- `frontend/app/login/page.tsx` — login form
- `frontend/app/register/page.tsx` — registration form

---

## DAY 6 — Application Forms & Documents ✅

**Objectives**
1. Dynamic form handling
2. Server-side and client-side validation
3. Document upload with type/size controls
4. Secure document storage (local filesystem; S3-ready)
5. Application status tracking

**What was built**
- `frontend/app/services/business-registration/page.tsx` — application form
- `frontend/app/dashboard/page.tsx` — citizen's application list
- `frontend/app/services/page.tsx` — service catalogue UI
- `backend/app/api/v1/routes/documents.py`:
  - `POST /applications/{id}/documents` — authenticated upload; validates extension, MIME type, size (10 MB max)
  - `GET /applications/{id}/documents` — list documents
  - `GET /applications/{id}/documents/{doc_id}/download` — serve file

---

## DAY 7 — Workflow Engine ✅

**Objectives**
1. Model the complete application lifecycle state machine
2. Implement state transitions with enforcement
3. Officer dashboard
4. Audit every transition

**State machine**
```
submitted → under_review → payment_pending → paid → officer_review → approved → completed
                         ↘ rejected (from any review state)
```

**What was built**
- `backend/app/api/v1/routes/officer.py`:
  - `GET /officer/applications` — list all applications (officer/admin only), filterable by status
  - `GET /officer/applications/{id}` — full application detail
  - `POST /officer/applications/{id}/transition` — advance through allowed states
  - `POST /officer/applications/{id}/review` — approve or reject (officer_review state only)
  - `POST /officer/applications/{id}/assign` — assign application to an officer via WorkflowTask
  - `GET /officer/applications/{id}/audit` — immutable audit trail
- `backend/app/schemas/officer.py` — all officer-facing request/response models
- Every transition creates an `AuditLog` record and queues a `Notification`
- Terminal states (approved, rejected, completed) are enforced; illegal transitions return 422

---

## DAY 8 — Payments & Notifications ✅

**Objectives**
1. Payment abstraction layer
2. Mock/sandbox payment provider
3. Payment status handling and audit
4. Email/SMS notification concepts
5. Background task dispatch

**What was built**
- `backend/app/api/v1/routes/payments.py`:
  - `POST /applications/{id}/payment` — initiates mock payment (RWF 50,000 flat fee); instantly completes and transitions application to `paid`
  - `GET /applications/{id}/payment` — retrieve payment status
- `backend/app/api/v1/routes/notifications.py`:
  - `GET /notifications/me` — citizen's notification history
  - `POST /notifications/dispatch` — admin-triggered background flush of queued notifications
  - Mock delivery provider logs notifications to stdout; real provider (SendGrid, Africa's Talking) replaces only `_mock_deliver`
- All status transitions queue a `Notification` row with `delivery_status='queued'`
- `BackgroundTasks` used for non-blocking dispatch

---

## DAY 9 — API Integration & Interoperability 🔄

**Objectives**
1. OpenAPI documentation (auto-generated by FastAPI at `/docs`)
2. External API integration patterns
3. Identity/payment/notification provider patterns
4. API keys and OAuth concepts
5. Retries, timeouts, and failure handling

**Planned tasks**
- [ ] Add API key authentication option alongside JWT
- [ ] Document webhook patterns for real payment callbacks
- [ ] Add `httpx` client with retry/timeout for outbound calls
- [ ] Export OpenAPI spec to `docs/openapi.json`

---

## DAY 10 — Security by Design 🔄

**Already implemented**
- Authentication: JWT Bearer, bcrypt (never plaintext)
- RBAC: per-route `require_role` dependency
- Object-level authorization: citizens can only access own records
- Input validation: Pydantic schemas on every endpoint
- CORS: explicit origin, method (`GET POST PUT PATCH DELETE OPTIONS`), header allow-lists
- Rate limiting: `slowapi` middleware (200 req/min default, Redis-backed in production)
- Audit logging: every state transition recorded with actor, from/to state, timestamp
- Secrets via environment variables (never hard-coded)
- Non-root Docker images for both services

**Remaining tasks**
- [ ] Add security headers middleware (X-Content-Type-Options, X-Frame-Options, HSTS)
- [ ] Input sanitization for free-text fields
- [ ] Implement `slowapi` Redis storage for distributed rate limiting
- [ ] Document threat model (STRIDE) in `docs/threat-model.md`
- [ ] Run OWASP Dependency-Check
- [ ] Add MFA/OTP concept implementation

---

## DAY 11 — Testing & Quality 🔄

**What was built**
- `backend/tests/conftest.py` — session-scoped Alembic migration, per-test rollback, fixtures: `db`, `client`, `citizen_user`, `officer_user`, `citizen_token`, `officer_token`, `biz_reg_service`
- `backend/tests/test_auth.py` — register, login, refresh, `/auth/me`, error cases
- `backend/tests/test_services.py` — catalogue endpoint coverage
- `backend/tests/test_applications.py` — create, list, detail, ownership isolation, audit log
- `backend/tests/test_workflow.py` — full happy-path workflow, state machine enforcement, audit trail

**Remaining tasks**
- [ ] Payment and notification endpoint tests
- [ ] Document upload tests
- [ ] Frontend unit tests (React Testing Library)
- [ ] Target ≥ 80% backend coverage (`pytest --cov=app`)

**Running tests**
```bash
cd backend
pytest -v --cov=app --cov-report=term-missing
```

---

## DAY 12 — Deployment & DevOps 🔄

**What was built**
- `backend/Dockerfile` — multi-stage (deps → production), non-root user, libpq
- `frontend/Dockerfile` — multi-stage (deps → builder → production), `node:20-alpine`, standalone output
- `frontend/next.config.mjs` — `output: "standalone"` enabled
- `docker-compose.yml` — postgres:16-alpine + redis:7-alpine with health checks
- `.github/workflows/backend-tests.yml` — lint, security scan, unit tests, mypy (Python 3.11 & 3.13)
- `.github/workflows/frontend-tests.yml` — ESLint, TypeScript check, build, npm audit
- `.github/workflows/deploy.yml` — builds and pushes backend + frontend images to GHCR
- `.github/workflows/db-migrations.yml` — runs Alembic on push
- `.github/workflows/quality.yml` — SonarCloud, OWASP, Codecov

**To run locally**
```bash
# Start dependencies
docker compose up -d

# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

**Remaining tasks**
- [ ] Add backend + frontend services to `docker-compose.yml` for full-stack local run
- [ ] HTTPS/TLS configuration guide
- [ ] Database backup strategy (pg_dump cron)
- [ ] Prometheus metrics endpoint

---

## DAY 13 — AI & Intelligent Services ⏳

**Planned**
- Document classification (identify ID cards, certificates from uploads)
- AI-assisted form pre-fill
- Fraud / anomaly detection on submissions
- Simple service assistant chatbot
- Human-in-the-loop: AI flags; officer decides

---

## DAY 14 — Capstone, Demo & Future Architecture ⏳

**Planned**
- Complete end-to-end citizen journey demo
- Officer dashboard walkthrough
- Security review against OWASP Top 10
- Performance discussion and bottleneck analysis
- Roadmap toward a national-scale production platform

---

## Target MVP Checklist

| Feature | Status |
|---|---|
| Citizen registration and login | ✅ |
| Service catalogue | ✅ |
| Online application form | ✅ |
| Document upload | ✅ |
| Application tracking | ✅ |
| Administrative / officer dashboard | ✅ |
| Approval/rejection workflow | ✅ |
| Payment simulation (mock) | ✅ |
| SMS/email notification simulation | ✅ |
| Digital document generation (certificate) | ⏳ Day 12 |
| Audit trail | ✅ |
| Automated test suite | ✅ (backend) / ⏳ (frontend) |
| Dockerized deployment | ✅ |
| CI/CD pipelines | ✅ |

---

## API Endpoint Summary

| Method | Path | Role | Description |
|---|---|---|---|
| GET | `/health` | public | Health check |
| POST | `/auth/register` | public | Create citizen account |
| POST | `/auth/token` | public | OAuth2 login |
| POST | `/auth/refresh` | public | Refresh tokens |
| GET | `/auth/me` | any auth | Current user identity |
| GET | `/services` | public | Service catalogue |
| POST | `/applications` | citizen | Submit application |
| GET | `/applications/me` | citizen | Own applications |
| GET | `/applications/{id}` | citizen | Own application detail |
| POST | `/applications/{id}/documents` | citizen | Upload document |
| GET | `/applications/{id}/documents` | citizen/officer | List documents |
| GET | `/applications/{id}/documents/{doc_id}/download` | citizen/officer | Download file |
| POST | `/applications/{id}/payment` | citizen | Initiate mock payment |
| GET | `/applications/{id}/payment` | citizen | Payment status |
| GET | `/notifications/me` | any auth | Notification history |
| POST | `/notifications/dispatch` | admin | Flush queued notifications |
| GET | `/officer/applications` | officer/admin | All applications (filterable) |
| GET | `/officer/applications/{id}` | officer/admin | Application detail |
| POST | `/officer/applications/{id}/transition` | officer/admin | Advance workflow state |
| POST | `/officer/applications/{id}/review` | officer/admin | Approve or reject |
| POST | `/officer/applications/{id}/assign` | officer/admin | Assign to officer |
| GET | `/officer/applications/{id}/audit` | officer/admin | Audit trail |

---

*SecureAI Labs — Secure Today. Empower Tomorrow.*  
*www.secureailabs.org*
