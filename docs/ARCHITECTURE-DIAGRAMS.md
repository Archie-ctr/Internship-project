# BizReg — System Architecture & Data Flow

> Digital Public Service Platform · SecureAI Labs  
> Built following the 14-Day Full-Stack Development Curriculum

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph CLIENT["Client Layer"]
        direction TB
        BROWSER["🌐 Web Browser\n(Desktop / Mobile)"]
    end

    subgraph FRONTEND["Frontend · Next.js 14 · :3000"]
        direction TB
        LP["Landing Page\n/"]
        AUTH_PAGES["Auth Pages\n/login  /register"]
        CITIZEN_UI["Citizen Portal\n/dashboard\n/services\n/services/business-registration"]
        OFFICER_UI["Officer Portal\n/officer"]
        ADMIN_UI["Admin Portal\n/admin"]
        HEADER["SiteHeader\n(auth-aware, role-aware)"]
        GUARD["ProtectedRoute\n(client-side guard)"]
        AUTH_LIB["lib/auth.ts\napiFetch · saveTokens\nclearTokens · getAccessToken"]
    end

    subgraph BACKEND["Backend · FastAPI · :8000"]
        direction TB
        MIDDLEWARE["Middleware Stack\nCORS · Rate Limiter (slowapi 200/min)\nSlowAPI"]
        ROUTER["API Router\n/api/v1"]

        subgraph ROUTES["Route Handlers"]
            R_HEALTH["GET /health"]
            R_AUTH["POST /auth/register\nPOST /auth/token\nPOST /auth/refresh\nGET  /auth/me"]
            R_SVC["GET /services"]
            R_APP["POST /applications\nGET  /applications/me\nGET  /applications/:id"]
            R_DOC["POST /applications/:id/documents\nGET  /applications/:id/documents\nGET  /applications/:id/documents/:id/download"]
            R_PAY["POST /applications/:id/payment\nGET  /applications/:id/payment"]
            R_NOTIF["GET  /notifications/me\nPOST /notifications/dispatch"]
            R_OFFICER["GET  /officer/applications\nGET  /officer/applications/:id\nPOST /officer/applications/:id/transition\nPOST /officer/applications/:id/review\nPOST /officer/applications/:id/assign\nGET  /officer/applications/:id/audit\nGET  /officer/users"]
        end

        subgraph DEPS["Dependencies / Security"]
            DEP_AUTH["get_current_user\n(JWT decode → DB lookup)"]
            DEP_ROLE["require_role(*roles)\n(RBAC factory)"]
        end

        subgraph SERVICES["Service Layer"]
            SVC_APP["application_service.py\ncreate_business_registration"]
        end

        subgraph CORE["Core"]
            SEC["security.py\nbcrypt hash/verify\nJWT create/decode"]
            CFG["config.py\npydantic-settings\nenv-based config"]
        end
    end

    subgraph DATA["Data Layer · Docker"]
        direction TB
        PG["🐘 PostgreSQL 16\nbizreg-postgres\nhost:5433 → container:5432"]
        REDIS["⚡ Redis 7\nbizreg-redis\nhost:6380 → container:6379"]
        STORAGE["📁 Local Storage\n./storage/documents\n(S3-ready abstraction)"]
    end

    subgraph ORM["ORM / Migrations"]
        ALEMBIC["Alembic\nMigrations\n20260827_0001"]
        SA["SQLAlchemy 2.0\nMapped / mapped_column"]
    end

    BROWSER -->|"HTTPS fetch()\nBearer token"| FRONTEND
    AUTH_PAGES --> AUTH_LIB
    CITIZEN_UI --> AUTH_LIB
    OFFICER_UI --> AUTH_LIB
    ADMIN_UI --> AUTH_LIB
    GUARD -->|"reads localStorage\npost-hydration only"| AUTH_LIB
    HEADER -->|"GET /auth/me\non mount"| AUTH_LIB

    AUTH_LIB -->|"REST / JSON\nAuthorization: Bearer"| MIDDLEWARE
    MIDDLEWARE --> ROUTER
    ROUTER --> ROUTES
    ROUTES --> DEPS
    DEPS --> SEC
    ROUTES --> SERVICES
    SERVICES --> SA
    SA --> PG
    ROUTES -->|"rate limit store"| REDIS
    ROUTES -->|"file write"| STORAGE
    SA -.->|"schema sync"| ALEMBIC
    ALEMBIC -.->|"CREATE TABLE\nSEED DATA"| PG
```

---

## 2. Request / Response Data Flow

### 2a. Citizen submits a business registration application

```mermaid
sequenceDiagram
    actor Citizen
    participant FE as Next.js Frontend
    participant MW as FastAPI Middleware
    participant RTE as POST /applications
    participant DEP as require_role("citizen")
    participant SEC as security.py
    participant SVC as application_service.py
    participant DB as PostgreSQL

    Citizen->>FE: Fills form & clicks Submit
    FE->>FE: Validates required fields (client-side)
    FE->>MW: POST /api/v1/applications\nAuthorization: Bearer <access_token>\nContent-Type: application/json

    MW->>MW: CORS check
    MW->>MW: Rate limit check (200/min per IP)
    MW->>RTE: Forward request

    RTE->>DEP: Resolve dependency
    DEP->>SEC: decode_token(access_token)
    SEC-->>DEP: {sub: uuid, role: "citizen", type: "access"}
    DEP->>DB: SELECT * FROM users WHERE id = uuid
    DB-->>DEP: User(role="citizen", is_active=True)
    DEP-->>RTE: current_user

    RTE->>DB: SELECT * FROM services\nWHERE code="business-registration"\nAND is_active=TRUE
    DB-->>RTE: Service

    RTE->>SVC: create_business_registration(db, citizen, service, payload)
    SVC->>DB: INSERT INTO applications\n(status_code="submitted", form_data=...)
    DB-->>SVC: Application(id=uuid)
    SVC->>DB: INSERT INTO audit_logs\n(action="application_created", to_state="submitted")
    DB-->>SVC: AuditLog
    SVC->>DB: COMMIT
    SVC-->>RTE: Application

    RTE->>DB: SELECT application JOIN service WHERE id=uuid
    DB-->>RTE: ApplicationResponse
    RTE-->>FE: 201 Created\n{id, status:"submitted", business_name, ...}

    FE->>FE: router.push("/dashboard")
    FE-->>Citizen: Dashboard shows new application
```

### 2b. Officer reviews and approves an application

```mermaid
sequenceDiagram
    actor Officer
    participant FE as Officer Dashboard
    participant API as FastAPI
    participant WF as POST /officer/applications/:id/review
    participant DEP as require_role("officer","admin")
    participant DB as PostgreSQL

    Officer->>FE: Opens application (status: officer_review)
    FE->>API: GET /api/v1/officer/applications/:id
    API->>DB: SELECT application + joins
    DB-->>API: ApplicationDetailOfficer
    API-->>FE: Full detail + form_data

    FE->>API: GET /api/v1/officer/applications/:id/audit
    DB-->>API: AuditLog[]
    API-->>FE: Audit trail

    Officer->>FE: Clicks "Approve"
    FE->>API: POST /officer/applications/:id/review\n{"decision": "approved"}

    API->>DEP: Verify officer/admin role
    DEP-->>API: current_officer

    API->>DB: UPDATE applications\nSET status_code="approved"\nregistration_number="BR-XXXXXXXX"
    API->>DB: INSERT INTO audit_logs\n(action="application_approved"\nfrom="officer_review", to="approved")
    API->>DB: INSERT INTO notifications\n(channel="email", delivery_status="queued"\nsubject="Application approved!")
    API->>DB: COMMIT
    DB-->>API: Updated ApplicationDetailOfficer

    API-->>FE: 200 OK {status:"approved", registration_number:"BR-..."}
    FE->>FE: Update row in table
    FE-->>Officer: Success — badge turns green
```

### 2c. Authentication flow (Login → JWT → Protected request)

```mermaid
sequenceDiagram
    actor User
    participant FE as Login Page
    participant API as POST /auth/token
    participant SEC as security.py
    participant DB as PostgreSQL
    participant LS as localStorage

    User->>FE: Enter email + password
    FE->>API: POST /auth/token\nContent-Type: application/x-www-form-urlencoded\nusername=email&password=pass

    API->>DB: SELECT user WHERE email=normalized_email
    DB-->>API: User(password_hash, role, is_active)

    API->>SEC: verify_password(plain, hash)\n[bcrypt.checkpw — constant time]
    SEC-->>API: True

    API->>SEC: create_access_token(user_id, role)\ncreate_refresh_token(user_id, role)
    SEC-->>API: JWT pair\n(HS256, exp: 30min / 7days)

    API-->>FE: 200 {access_token, refresh_token, token_type:"bearer"}

    FE->>LS: saveTokens(access_token, refresh_token)
    FE->>FE: router.push("/dashboard")

    Note over FE,LS: On every subsequent request:
    FE->>LS: getAccessToken()
    LS-->>FE: access_token
    FE->>API: GET /auth/me\nAuthorization: Bearer <access_token>
    API->>SEC: decode_token → verify type=="access"
    API->>DB: SELECT user WHERE id=sub (live check)
    DB-->>API: User
    API-->>FE: {email, full_name, role, is_active}
```

---

## 3. Database Schema & Relationships

```mermaid
erDiagram
    roles {
        int id PK
        string name UK "citizen | officer | admin"
        string description
    }

    users {
        uuid id PK
        string email UK
        string full_name
        string password_hash "bcrypt, never plaintext"
        int role_id FK
        bool is_active
        datetime created_at
    }

    services {
        int id PK
        string code UK
        string name
        text description
        bool is_active
        datetime created_at
    }

    application_statuses {
        string code PK "submitted | under_review | payment_pending | paid | officer_review | approved | rejected | completed"
        string label
        text description
    }

    applications {
        uuid id PK
        uuid citizen_id FK
        int service_id FK
        string status_code FK
        json form_data
        string registration_number UK
        text rejection_reason
        datetime created_at
    }

    documents {
        uuid id PK
        uuid application_id FK
        string document_type
        string original_filename
        string storage_key UK
        string content_type
        int size_bytes
        datetime created_at
    }

    payments {
        uuid id PK
        uuid application_id UK "one-to-one"
        string provider "mock | mtn_momo | stripe"
        string provider_reference UK
        decimal amount "12,2"
        string currency "RWF"
        string status "pending | completed | failed"
        datetime created_at
    }

    notifications {
        uuid id PK
        uuid user_id FK
        string channel "email | sms"
        string recipient
        string subject
        text body
        string delivery_status "queued | delivered | failed"
        datetime created_at
    }

    workflow_tasks {
        uuid id PK
        uuid application_id FK
        uuid assigned_officer_id FK
        string task_type "review"
        string status "open | reassigned | closed"
        text notes
        datetime created_at
    }

    audit_logs {
        uuid id PK
        uuid application_id FK
        uuid actor_id FK
        string action
        string from_state
        string to_state
        json details
        datetime created_at "append-only"
    }

    roles            ||--o{ users               : "has role"
    users            ||--o{ applications         : "citizen submits"
    services         ||--o{ applications         : "belongs to"
    application_statuses ||--o{ applications     : "current status"
    applications     ||--o{ documents            : "has documents"
    applications     ||--|| payments             : "has one payment"
    applications     ||--o{ notifications        : "triggers"
    users            ||--o{ notifications        : "receives"
    applications     ||--o{ workflow_tasks       : "assigned via"
    users            ||--o{ workflow_tasks       : "officer handles"
    applications     ||--o{ audit_logs           : "tracked by"
    users            ||--o{ audit_logs           : "actor"
```

---

## 4. Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> submitted : Citizen submits form

    submitted --> under_review   : Officer picks up
    submitted --> rejected       : Officer rejects immediately

    under_review --> payment_pending : Documents verified
    under_review --> rejected        : Documents incomplete

    payment_pending --> paid     : Citizen pays RWF 50,000\n(mock sandbox)
    payment_pending --> rejected : Officer rejects

    paid --> officer_review      : Officer begins final review
    paid --> rejected            : Officer rejects

    officer_review --> approved  : Officer approves\n→ registration_number generated
    officer_review --> rejected  : Officer rejects\n(reason required)

    approved --> completed       : Certificate issued

    rejected --> [*]
    completed --> [*]

    note right of submitted
        AuditLog created
        Notification queued
    end note

    note right of approved
        registration_number = BR-XXXXXXXX
        AuditLog created
        Notification: "Application approved!"
    end note
```

---

## 5. Security Architecture

```mermaid
graph LR
    subgraph TRANSPORT["Transport Security"]
        TLS["TLS 1.3\n(HTTPS in production)"]
    end

    subgraph IDENTITY["Identity & Auth"]
        BCRYPT["bcrypt\nPassword Hashing\n12 rounds"]
        JWT_A["JWT Access Token\nHS256 · 30 min"]
        JWT_R["JWT Refresh Token\nHS256 · 7 days"]
        DECODE["decode_token()\ntype check\n+ live DB user lookup"]
    end

    subgraph AUTHZ["Authorization (RBAC)"]
        GUARD_CITIZEN["require_role('citizen')"]
        GUARD_OFFICER["require_role('officer','admin')"]
        GUARD_ADMIN["require_role('admin')"]
        OBJ_AUTH["Object-level auth\ncitizen_id == current_user.id"]
    end

    subgraph INPUT["Input Validation"]
        PYDANTIC["Pydantic v2 Schemas\nRequest body validation\nType coercion"]
        FILE_VAL["File Validation\nMIME type · Extension\nMax 10 MB"]
    end

    subgraph RATE["Rate Limiting"]
        SLOWAPI["slowapi\n200 req/min per IP\n429 on exceed"]
    end

    subgraph AUDIT["Audit & Observability"]
        AUDIT_LOG["AuditLog table\nEvery state transition\nActor · from → to · timestamp"]
        NOTIF["Notification queue\nEvery status change"]
    end

    subgraph SECRETS["Secrets Management"]
        ENV[".env (never committed)\nJWT_SECRET_KEY\nDATABASE_URL\nPOSTGRES_PASSWORD"]
        PYDANTIC_CFG["pydantic-settings\nType-safe config\nFails fast on missing vars"]
    end

    TLS --> IDENTITY
    BCRYPT --> JWT_A
    JWT_A --> DECODE
    JWT_R --> DECODE
    DECODE --> AUTHZ
    PYDANTIC --> AUTHZ
    AUTHZ --> AUDIT_LOG
    FILE_VAL --> OBJ_AUTH
    RATE --> AUDIT_LOG
    ENV --> PYDANTIC_CFG
```

---

## 6. Deployment Architecture

```mermaid
graph TB
    subgraph DEV["Development (local)"]
        direction LR
        NEXT_DEV["next dev\n:3000"]
        UVICORN["uvicorn --reload\n:8000"]
        DC["docker compose up\npostgres:5433\nredis:6380"]
        NEXT_DEV <-->|"REST API calls"| UVICORN
        UVICORN <-->|"SQLAlchemy / psycopg3"| DC
    end

    subgraph CI["CI/CD · GitHub Actions"]
        direction TB
        LINT["backend-tests.yml\nblack · isort · flake8\nbandit · safety\npytest · mypy"]
        FE_CI["frontend-tests.yml\nESLint · Prettier\ntsc · next build\nnpm audit"]
        QUALITY["quality.yml\nSonarCloud\nOWASP\nCodecov"]
        DEPLOY["deploy.yml\nDocker image build\nPush → GHCR"]
        MIGRATE["db-migrations.yml\nalembic upgrade head"]
    end

    subgraph PROD["Production (target)"]
        direction TB
        NGINX["NGINX / Reverse Proxy\nTLS termination\n:443"]
        FE_PROD["Next.js\nstandalone output\nDocker container"]
        BE_PROD["FastAPI + Uvicorn\nDocker container\nnon-root user"]
        PG_PROD["PostgreSQL 16\nmanaged or container\nencrypted volume"]
        REDIS_PROD["Redis 7\nrate limit store\nsession cache"]
        S3["S3-compatible\nDocument storage\n(MinIO / AWS S3)"]

        NGINX -->|":3000"| FE_PROD
        NGINX -->|":8000"| BE_PROD
        BE_PROD -->|"psycopg3"| PG_PROD
        BE_PROD -->|"redis-py"| REDIS_PROD
        BE_PROD -->|"storage abstraction"| S3
    end

    DEV -.->|"git push"| CI
    CI -.->|"on merge to main"| PROD
```

---

## 7. Frontend Component Architecture

```mermaid
graph TB
    subgraph LAYOUT["RootLayout (app/layout.tsx)"]
        HEADER["SiteHeader\nauth-aware · role-aware\nhamburger menu on mobile"]
        CHILDREN["Page Content"]
        FOOTER["Footer"]
    end

    subgraph PAGES["Pages (Next.js App Router)"]
        PG_HOME["/ Landing Page\n(server component)"]
        PG_LOGIN["/login\nDemo account fill-in\nOAuth2 form-urlencoded"]
        PG_REG["/register\nPassword validation\nJSON registration"]
        PG_DASH["/dashboard\nCitizen portal\nstats · apps · notifications"]
        PG_SVC["/services\nService catalogue"]
        PG_FORM["/services/business-registration\nGuided multi-section form\n2-col responsive grid"]
        PG_OFF["/officer\nApplication queue\nSearch · filter · slide-over"]
        PG_ADM["/admin\n4-tab dashboard\nOverview·Apps·Users·Notifs"]
    end

    subgraph COMPONENTS["Shared Components"]
        PR["ProtectedRoute\nstate: null→false→true\nno hydration mismatch"]
        SH["SiteHeader\nrole-based links\nhamburger for mobile"]
    end

    subgraph LIB["lib/auth.ts"]
        API_FETCH["apiFetch()\nauto Bearer token"]
        TOKENS["saveTokens()\ngetAccessToken()\nclearTokens()"]
        API_URL["getApiUrl()\nNEXT_PUBLIC_API_URL"]
    end

    LAYOUT --> HEADER
    LAYOUT --> CHILDREN
    LAYOUT --> FOOTER

    CHILDREN --> PG_HOME
    CHILDREN --> PG_LOGIN
    CHILDREN --> PG_REG
    CHILDREN --> PG_DASH
    CHILDREN --> PG_SVC
    CHILDREN --> PG_FORM
    CHILDREN --> PG_OFF
    CHILDREN --> PG_ADM

    PG_DASH --> PR
    PG_SVC --> PR
    PG_FORM --> PR
    PG_OFF --> PR
    PG_ADM --> PR

    PG_DASH --> API_FETCH
    PG_OFF --> API_FETCH
    PG_ADM --> API_FETCH
    PG_FORM --> API_FETCH
    PG_SVC --> API_FETCH

    API_FETCH --> TOKENS
    API_FETCH --> API_URL

    HEADER --> SH
    PR --> COMPONENTS
```

---

## Summary Table

| Layer | Technology | Version | Role |
|---|---|---|---|
| Frontend | Next.js (App Router) | 14.2 | UI, routing, SSR |
| Frontend lang | TypeScript | 5.8 | Type safety |
| Styling | Tailwind CSS | 3.4 | Responsive design |
| Backend | FastAPI | 0.115 | REST API, validation |
| Backend lang | Python | 3.13 | Business logic |
| Server | Uvicorn | 0.34 | ASGI server |
| ORM | SQLAlchemy | 2.0 | DB abstraction |
| Migrations | Alembic | 1.15 | Schema versioning |
| DB driver | psycopg (v3) | 3.2 | PostgreSQL adapter |
| Database | PostgreSQL | 16 | Primary data store |
| Cache / Rate | Redis | 7 | Rate limit store |
| Auth | PyJWT + bcrypt | 2.10 / 4.2 | JWT + password hashing |
| Validation | Pydantic v2 | 2.x | Schema validation |
| Rate limiting | slowapi | 0.1.9 | 200 req/min per IP |
| Containerisation | Docker + Compose | — | Local infra |
| CI/CD | GitHub Actions | — | 5 workflows |
| Registry | GHCR | — | Docker image push |
