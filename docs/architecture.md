# Architecture and design decisions

## Request lifecycle

The following sequence is the current happy path for submitting an application:

```text
1. Citizen signs in at /login.
2. Next.js sends form-urlencoded credentials to POST /api/v1/auth/token.
3. FastAPI verifies the bcrypt password hash and returns access + refresh JWTs.
4. The browser stores the pair locally for this learning phase.
5. Citizen opens /services and chooses Business Registration.
6. The form sends validated JSON plus `Authorization: Bearer <access token>`.
7. FastAPI verifies the JWT, reloads the user and role from PostgreSQL,
   validates the form body, and checks the citizen role.
8. The application service writes the Application and AuditLog in one commit.
9. The dashboard requests only GET /applications/me and displays the result.
```

## API layering

| Layer | Responsibility | Example |
| --- | --- | --- |
| `api/v1/routes` | Translate HTTP into validated use-case calls | `applications.py` |
| `api/deps.py` | Identity, database session, and RBAC dependencies | `require_role("citizen")` |
| `schemas` | Validate untrusted input and control response shape | `CreateBusinessRegistrationRequest` |
| `services` | Business actions and transaction boundaries | `create_business_registration` |
| `models` | SQLAlchemy mapping and relational integrity | `Application`, `AuditLog` |
| `db` | Engine, sessions, Alembic metadata | `SessionLocal`, `Base` |

Routes should stay comparatively small. For example, the application route finds the active service and calls `create_business_registration`; the service function owns the database transaction and initial audit entry. This makes business behaviour easier to test without HTTP later.

## Authentication design

Passwords are bcrypt hashes, never plaintext. Login uses FastAPI's `OAuth2PasswordRequestForm`, so its `username` field contains the email. JWTs carry:

- `sub`: user UUID, not the email address
- `role`: role name when issued
- `type`: either `access` or `refresh`
- `iat` and `exp`: issued and expiry time

An access token alone is not sufficient for a protected action. `get_current_user` verifies its signature and type, then reloads the user and role from the database. This lets a disabled account or changed role take effect before token expiry. `require_role` is used on every role-restricted route; hiding a frontend button is not authorisation.

Refresh tokens are stateless in the current learning implementation. A production implementation should use token family IDs, a revocation store, rotation/reuse detection, and secure HttpOnly cookies.

## Data model

```text
Role 1 ---- * User 1 ---- * Application * ---- 1 Service
                         |       |
                         |       +---- 1 ApplicationStatus
                         |
                         +---- * Document         (future upload implementation)
                         +---- 0..1 Payment       (future payment implementation)
                         +---- * WorkflowTask     (future officer workflow)
                         +---- * AuditLog

User 1 ---- * Notification                         (future notification implementation)
User 1 ---- * AuditLog (actor)
```

`Application.form_data` is JSON because service-specific form fields evolve; ownership, service, and state are relational columns because they require strong integrity and efficient filtering. The application status lookup table holds legal state labels. A later explicit state machine will define legal *transitions* between them.

## Workflow state design

The target lifecycle is:

```text
submitted -> under_review -> payment_pending -> paid -> officer_review
                                                  -> approved -> completed
                                                  -> rejected
```

Today, only `submitted` is created. Phase 6 will introduce the transition rules in a dedicated module and write an `AuditLog` row with actor, action, timestamp, old state, and new state for every state change. The current creation audit entry establishes the same evidence pattern.

## Infrastructure

`docker-compose.yml` currently owns only durable local dependencies:

- PostgreSQL 16 on `localhost:5432`, persisted in the `postgres_data` volume
- Redis 7 on `localhost:6379`, persisted in the `redis_data` volume

PostgreSQL is the source of truth. Redis is provisioned now for later rate limiting, caching, or queues; no current route depends on it. Phase 11 will add frontend and backend Dockerfiles and bring all services up with one Compose command.

## Cross-origin browser access

In local development, Next.js (`localhost:3000`) and FastAPI (`localhost:8000`) are different origins. FastAPI CORS middleware allows only the configured `BACKEND_CORS_ORIGINS` values, defaulting to `http://localhost:3000`. It allows only the request methods and headers currently needed. Phase 9 will review this together with security headers, rate limiting, production TLS, and deployment configuration.
