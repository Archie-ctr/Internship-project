# Day 1: Problem, Requirements & Architecture

## 1. Understanding Digital Public-Service Platforms

### What is a Digital Public-Service Platform?

A digital public-service platform is a government digital transformation initiative that enables citizens to:
- Access government services online without physical office visits
- Apply for licenses, permits, registrations, and certifications digitally
- Track application status in real-time
- Submit required documents electronically
- Make payments online
- Receive official communications and certificates

### Real-World Examples
- **Irembo (Rwanda)**: Model platform for African government digitization
- **GovTech (Singapore)**: Integrated government service delivery
- **Estonia e-Residency**: Fully digital services
- **India's Digital Platform**: Aadhaar and e-governance initiatives

### Value Proposition
| Stakeholder | Benefits |
|---|---|
| **Citizens** | Convenience, speed, transparency, accessibility 24/7 |
| **Government** | Reduced manual work, audit trails, cost savings, efficiency |
| **Officers** | Clear workflow, prioritized applications, better data |

---

## 2. MVP Service Selection: Business Registration

### Why Business Registration?

Selected for MVP due to:
- **Scope**: Complete but manageable workflow (~6-8 steps)
- **Impact**: Critical government service for business enablement
- **Transferability**: Pattern applies to other services (licenses, permits)
- **Testing**: Natural workflow with clear success criteria

### Business Registration Workflow (Citizen → Government)

```
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS REGISTRATION WORKFLOW                  │
└─────────────────────────────────────────────────────────────┘

STEP 1: DISCOVERY & AUTHENTICATION
  ├─ Citizen visits platform
  ├─ Creates account (email, password, basic details)
  └─ Logs in with credentials

STEP 2: SERVICE SELECTION
  ├─ Browses available government services
  └─ Selects "Business Registration"

STEP 3: APPLICATION FORM
  ├─ Completes structured form with:
  │  ├─ Business name & type
  │  ├─ Business address & operating location
  │  ├─ Owner/director details
  │  ├─ Proposed business activities
  │  └─ Contact information
  └─ Form validation in real-time

STEP 4: DOCUMENT SUBMISSION
  ├─ Uploads required documents:
  │  ├─ Business plan
  │  ├─ Owner ID/Passport
  │  └─ Proof of residence
  └─ System stores securely

STEP 5: PAYMENT (if applicable)
  ├─ System calculates registration fees
  ├─ Citizen makes payment
  └─ Payment receipt issued

STEP 6: APPLICATION SUBMISSION
  ├─ Citizen reviews and submits
  ├─ System records submission timestamp
  └─ Audit log entry created

STEP 7: TRACKING & NOTIFICATION
  ├─ Application appears on citizen dashboard
  ├─ Citizen receives confirmation email
  └─ Status updates sent for each state change:
     ├─ Submitted → Under Review
     ├─ Under Review → Payment Pending
     ├─ Payment Pending → Paid
     ├─ Paid → Officer Review
     ├─ Officer Review → Approved/Rejected
     └─ Approved → Certificate Issued

STEP 8: COMPLETION
  ├─ Officer approves application
  ├─ System generates registration certificate
  ├─ Certificate sent to citizen
  └─ Business officially registered
```

### Application Lifecycle States
```
submitted 
    ↓
under_review 
    ↓
payment_pending 
    ├─→ paid → officer_review ┐
    │                          ├─→ approved → completed
    └─→ rejected ──────────→ (Application rejected, citizen notified)
```

---

## 3. Functional Requirements

### User Stories

#### 3.1 Citizen Registration & Authentication
| ID | Requirement | Status |
|---|---|---|
| FR-1.1 | Citizen can register with email and strong password | ✅ Implemented (Phase 3) |
| FR-1.2 | System validates email format and password strength | ✅ Implemented (Phase 3) |
| FR-1.3 | Passwords hashed using bcrypt with salt | ✅ Implemented (Phase 3) |
| FR-1.4 | Citizen can login with email/password | ✅ Implemented (Phase 3) |
| FR-1.5 | System issues access & refresh JWT tokens | ✅ Implemented (Phase 3) |
| FR-1.6 | System validates token signature and expiry | ✅ Implemented (Phase 3) |
| FR-1.7 | Account status changes take effect immediately | ✅ Implemented (Phase 3) |

#### 3.2 Service Catalogue
| ID | Requirement | Status |
|---|---|---|
| FR-2.1 | System displays list of available services | ✅ Implemented (Phase 1) |
| FR-2.2 | Services loaded from database | ✅ Implemented (Phase 2) |
| FR-2.3 | "Business Registration" is seeded as primary MVP service | ✅ Implemented (Phase 2) |
| FR-2.4 | Citizens can filter/search services | 🔄 Planned (Phase 5+) |

#### 3.3 Business Registration Application
| ID | Requirement | Status |
|---|---|---|
| FR-3.1 | Citizen can access Business Registration form | ✅ Implemented (Phase 4) |
| FR-3.2 | Form captures: business name, type, address, activities | ✅ Implemented (Phase 4) |
| FR-3.3 | Form validates all required fields | ✅ Implemented (Phase 4) |
| FR-3.4 | Form data stored as JSON in database | ✅ Implemented (Phase 4) |
| FR-3.5 | Citizen can submit completed application | ✅ Implemented (Phase 4) |
| FR-3.6 | System records submission timestamp | ✅ Implemented (Phase 4) |
| FR-3.7 | Only citizens (not officers/admins) can submit as applicants | ✅ Implemented (Phase 3-4) |

#### 3.4 Application Dashboard
| ID | Requirement | Status |
|---|---|---|
| FR-4.1 | Citizen can view all their applications | ✅ Implemented (Phase 4) |
| FR-4.2 | Dashboard shows application status | ✅ Implemented (Phase 4) |
| FR-4.3 | Dashboard shows submission date | ✅ Implemented (Phase 4) |
| FR-4.4 | Citizen can only see their own applications | ✅ Implemented (Phase 4) |

#### 3.5 Document Management
| ID | Requirement | Status |
|---|---|---|
| FR-5.1 | Citizens can upload required documents | 🔄 Planned (Phase 5) |
| FR-5.2 | System scans for viruses | 🔄 Planned (Phase 5) |
| FR-5.3 | Documents stored securely with encryption | 🔄 Planned (Phase 5) |
| FR-5.4 | Officers can access documents for review | 🔄 Planned (Phase 5) |

#### 3.6 Officer Workflow
| ID | Requirement | Status |
|---|---|---|
| FR-6.1 | Officer dashboard shows assigned applications | 🔄 Planned (Phase 6+) |
| FR-6.2 | Officer can transition application state | 🔄 Planned (Phase 6) |
| FR-6.3 | Officer can add comments/requirements | 🔄 Planned (Phase 6+) |
| FR-6.4 | Officer can approve/reject application | 🔄 Planned (Phase 6+) |

#### 3.7 Notifications
| ID | Requirement | Status |
|---|---|---|
| FR-7.1 | Citizen receives email on application submission | 🔄 Planned (Phase 7) |
| FR-7.2 | Citizen receives email on status change | 🔄 Planned (Phase 7) |
| FR-7.3 | Citizen receives SMS notifications (optional) | 🔄 Planned (Phase 8+) |

#### 3.8 Payments
| ID | Requirement | Status |
|---|---|---|
| FR-8.1 | System calculates registration fees | 🔄 Planned (Phase 9) |
| FR-8.2 | Citizen can pay online via payment gateway | 🔄 Planned (Phase 9) |
| FR-8.3 | Payment status updated in application | 🔄 Planned (Phase 9) |

#### 3.9 Certificates
| ID | Requirement | Status |
|---|---|---|
| FR-9.1 | System generates PDF certificate on approval | 🔄 Planned (Phase 10) |
| FR-9.2 | Certificate includes registration number | 🔄 Planned (Phase 10) |
| FR-9.3 | Citizen can download certificate | 🔄 Planned (Phase 10) |

---

## 4. Non-Functional Requirements

### 4.1 Performance
| Requirement | Target | Status |
|---|---|---|
| Page load time (frontend) | < 2 seconds | ✅ Next.js optimized |
| API response time | < 200ms (P95) | ✅ FastAPI async |
| Database query performance | < 100ms per query | 🔄 Indexing planned |
| Concurrent users | 100+ (local dev) | ✅ Scalable architecture |

### 4.2 Security
| Requirement | Status |
|---|---|
| Passwords hashed with bcrypt | ✅ Implemented |
| OAuth2 JWT tokens | ✅ Implemented |
| HTTPS in production (HTTP local) | 🔄 Phase 11 |
| CORS configured (allow only frontend origin) | ✅ Implemented |
| Input validation & sanitization | ✅ Pydantic schemas |
| Role-Based Access Control (RBAC) | ✅ Implemented (3 roles: citizen, officer, admin) |
| SQL injection prevention (parameterized queries) | ✅ SQLAlchemy ORM |
| XSS protection (React auto-escaping) | ✅ Next.js |
| CSRF protection (future: SameSite cookies) | 🔄 Phase 9 |
| Rate limiting | 🔄 Planned (Redis) |
| Document encryption at rest | 🔄 Phase 5 |

### 4.3 Reliability & Availability
| Requirement | Status |
|---|---|
| Health check endpoint `/api/v1/health` | ✅ Implemented |
| Database connection pooling | ✅ SQLAlchemy |
| Graceful error handling | ✅ FastAPI exception handlers |
| Audit logging for all state changes | ✅ Implemented |
| Database backups (planned) | 🔄 Phase 11 |
| 99.5% uptime SLA (target) | 🔄 Production deployment |

### 4.4 Scalability
| Requirement | Status |
|---|---|
| Stateless API design (horizontal scaling) | ✅ Designed |
| Redis caching layer (provisioned) | ✅ Docker setup |
| Database read replicas (future) | 🔄 Phase 11+ |
| CDN for static assets (future) | 🔄 Phase 11+ |
| Load balancing (future) | 🔄 Production |

### 4.5 Maintainability
| Requirement | Status |
|---|---|
| Code organized by feature (routes, models, services, schemas) | ✅ Implemented |
| Separation of concerns (API layer, business logic, data) | ✅ Implemented |
| API versioning (`/api/v1/`) | ✅ Implemented |
| Database migrations (Alembic) | ✅ Implemented |
| Study notes for each phase | ✅ Phase 1-4 docs |
| Automated tests | 🔄 Phase 8+ |

### 4.6 Usability
| Requirement | Status |
|---|---|
| Mobile-responsive design (Tailwind CSS) | ✅ Implemented |
| Clear error messages | ✅ Pydantic validation |
| Form validation feedback | ✅ React forms |
| Accessibility features (WCAG 2.1 AA) | 🔄 Phase 9+ |
| Multiple language support (i18n) | 🔄 Phase 10+ |

### 4.7 Compliance & Audit
| Requirement | Status |
|---|---|
| Audit trail for all state changes | ✅ AuditLog model |
| Data privacy (GDPR-ready structure) | 🔄 Phase 9+ |
| Document retention policies | 🔄 Phase 11+ |
| Regulatory compliance (localized) | 🔄 Phase 12+ |

---

## 5. System Architecture & Data Flow

### 5.1 High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     CITIZEN BROWSER                            │
│              (Windows, Mac, iOS, Android)                      │
└────────────────┬─────────────────────────────────────────────────┘
                 │ HTTPS (Production) / HTTP (Local)
                 │ JSON REST API + Bearer Token
                 │ 
┌────────────────▼─────────────────────────────────────────────────┐
│            NEXT.JS FRONTEND (Port 3000)                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Pages:                                                    │  │
│  │  ├─ /                    (Landing)                         │  │
│  │  ├─ /login               (Sign-in)                         │  │
│  │  ├─ /register            (Account creation)                │  │
│  │  ├─ /dashboard           (Citizen's applications)          │  │
│  │  └─ /services            (Catalogue & forms)               │  │
│  │                                                            │  │
│  │  Components:                                              │  │
│  │  ├─ SiteHeader           (Navigation)                      │  │
│  │  ├─ ProtectedRoute       (Auth guard)                      │  │
│  │  └─ Forms                (Registration, Application)       │  │
│  │                                                            │  │
│  │  Utilities:                                               │  │
│  │  └─ lib/auth.ts          (Token storage, fetch helper)    │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────────┘
                 │ POST /api/v1/auth/token
                 │ GET /api/v1/auth/me
                 │ POST /api/v1/applications
                 │ GET /api/v1/applications/me
                 │ GET /api/v1/services
                 │ GET /api/v1/health
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│         FASTAPI BACKEND (Port 8000)                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  API Layer (app/api/v1/)                                  │  │
│  │  ├─ routes/auth.py         (Login, registration)          │  │
│  │  ├─ routes/applications.py (CRUD applications)            │  │
│  │  ├─ routes/services.py     (List services)                │  │
│  │  └─ routes/health.py       (Health check)                 │  │
│  │                                                            │  │
│  │  Dependencies (app/api/deps.py)                           │  │
│  │  ├─ get_current_user()     (JWT verification)             │  │
│  │  ├─ require_role()         (RBAC enforcement)             │  │
│  │  └─ get_db()               (Database session)             │  │
│  │                                                            │  │
│  │  Schemas (app/schemas/)                                   │  │
│  │  ├─ UserRegisterRequest    (Validation)                   │  │
│  │  ├─ TokenResponse          (Response shape)               │  │
│  │  └─ ApplicationSchema      (Form data validation)         │  │
│  │                                                            │  │
│  │  Services (app/services/)                                 │  │
│  │  ├─ application_service.py (Business logic)               │  │
│  │  └─ ... (more services as needed)                         │  │
│  │                                                            │  │
│  │  Models (app/models/)                                     │  │
│  │  ├─ User                                                  │  │
│  │  ├─ Application                                           │  │
│  │  ├─ Service                                               │  │
│  │  ├─ ApplicationStatus                                     │  │
│  │  ├─ AuditLog                                              │  │
│  │  ├─ Role                                                  │  │
│  │  └─ ... (other domain models)                             │  │
│  │                                                            │  │
│  │  Database Layer (app/db/)                                 │  │
│  │  ├─ session.py  (SQLAlchemy session)                      │  │
│  │  └─ base.py     (Declarative base & metadata)             │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────────┘
                 │ SQL (Parameterized)
                 │ Transactions
                 │
    ┌────────────┴─────────────────┬────────────────────┐
    │                              │                    │
┌───▼────────────┐   ┌────────────▼──┐   ┌────────────▼──┐
│  PostgreSQL    │   │  Redis (7.0)   │   │ Alembic        │
│  (Port 5432)   │   │ (Port 6379)    │   │ Migrations     │
│                │   │                │   │                │
│ ┌────────────┐ │   │ ┌────────────┐ │   │ ┌────────────┐ │
│ │ users      │ │   │ │ Cache      │ │   │ │ versions/  │ │
│ │ roles      │ │   │ │ Sessions   │ │   │ │ ...schema  │ │
│ │ services   │ │   │ │ Queues     │ │   │ │ .py        │ │
│ │ applications  │   │ │ Rate-limit │ │   │ └────────────┘ │
│ │ audit_logs │ │   │ │ (future)   │ │   │                │
│ │ documents  │ │   │ │            │ │   │                │
│ │ payments   │ │   │ │            │ │   │                │
│ │ ...        │ │   │ └────────────┘ │   │ ┌────────────┐ │
│ └────────────┘ │   │                │   │ │ Source of  │ │
│                │   │                │   │ │ Truth      │ │
└────────────────┘   └────────────────┘   └────────────────┘
```

### 5.2 Data Flow: Complete Application Submission

```
USER ACTION → HTTP REQUEST → API HANDLER → VALIDATION → BUSINESS LOGIC → DATABASE

1. CITIZEN SUBMITS FORM ON FRONTEND
   └─ User clicks "Submit Application"
   └─ Browser calls: POST /api/v1/applications
   └─ Payload: { business_name, type, address, form_data: {...} }
   └─ Header: Authorization: Bearer {access_token}

2. FASTAPI ROUTE HANDLER
   └─ routes/applications.py::create_application()
   └─ Depends(get_current_user) → Verifies JWT
   └─ Depends(require_role("citizen")) → Checks role
   └─ Receives: CreateApplicationRequest schema

3. INPUT VALIDATION
   └─ Pydantic schema validates all fields
   └─ Sanitizes input
   └─ Checks business_name length, type enum, address format
   └─ Returns validation error if invalid (HTTP 422)

4. DATABASE TRANSACTION
   └─ Gets database session from deps
   └─ Finds active Service by code "business-registration"
   └─ Gets ApplicationStatus "submitted" from reference table
   └─ Creates Application record with:
      ├─ user_id = current_user.id
      ├─ service_id = business_registration.id
      ├─ status_id = submitted.id
      ├─ form_data = validated form JSON
      └─ created_at = now()

5. AUDIT LOG ENTRY
   └─ Same transaction writes AuditLog:
      ├─ application_id = newly created app
      ├─ actor_id = current_user.id
      ├─ action = "application_created"
      ├─ old_state = null
      ├─ new_state = "submitted"
      └─ timestamp = now()

6. DATABASE COMMIT
   └─ Transaction commits (both Application + AuditLog)
   └─ PostgreSQL assigns id & timestamps
   └─ Returns Application object to API

7. API RESPONSE
   └─ Returns HTTP 201 Created
   └─ Body: ApplicationResponse schema
   └─ Includes: id, user_id, service_id, status, form_data, created_at

8. FRONTEND RECEIVES RESPONSE
   └─ JavaScript processes response
   └─ Updates UI state
   └─ Redirects to dashboard
   └─ Fetches GET /api/v1/applications/me
   └─ Lists all citizen's applications with new submission visible
```

### 5.3 Application Layering

```
┌──────────────────────────────────────────────────────────────┐
│ WEB TIER: Next.js Browser Pages & Components                 │
│ - Handles UI/UX                                              │
│ - Form validation (client-side for UX)                       │
│ - Token storage (localStorage)                               │
│ - HTTP requests via fetch + Bearer token                     │
└──────────────────────────────────────────────────────────────┘
                           ↓
                    HTTP/JSON/REST
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ API TIER: FastAPI Routes & Endpoints                         │
│ - Translate HTTP into business operations                    │
│ - JWT verification & RBAC enforcement                        │
│ - Input validation (server-side, authoritative)              │
│ - Route → Dependency injection (auth, db session)            │
│ - Dependency chain example:                                  │
│   POST /applications requires:                              │
│   ├─ get_current_user (JWT verification)                    │
│   ├─ require_role("citizen")                                │
│   └─ get_db (database session)                              │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ SERVICE TIER: Business Logic & Transactions                  │
│ - Create business registration application                   │
│ - Validate business rules (service exists, user is citizen) │
│ - Manage database transaction boundaries                     │
│ - Write audit logs                                           │
│ - Example: create_business_registration():                   │
│   ├─ Load Service from DB                                    │
│   ├─ Create Application record                               │
│   ├─ Create AuditLog record                                  │
│   └─ Commit transaction atomically                           │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ DATA TIER: SQLAlchemy ORM & Models                           │
│ - Define relational schema                                   │
│ - Foreign key constraints at database level                  │
│ - Parameterized queries (prevent SQL injection)              │
│ - SQLAlchemy models map to PostgreSQL tables:                │
│   ├─ User (id, email, password_hash, role_id, ...)         │
│   ├─ Application (id, user_id, service_id, status_id, ...)  │
│   ├─ Service (id, code, name, description, ...)             │
│   ├─ ApplicationStatus (id, code, name, description, ...)    │
│   ├─ AuditLog (id, application_id, actor_id, action, ...)   │
│   └─ ... (other domain models)                              │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ DATABASE TIER: PostgreSQL                                    │
│ - Persistent data storage                                    │
│ - ACID transactions                                          │
│ - Foreign key enforcement                                    │
│ - Alembic version tracking                                   │
│ - Seeded reference data (roles, services, statuses)          │
└──────────────────────────────────────────────────────────────┘
```

### 5.4 Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  REGISTRATION FLOW                          │
└─────────────────────────────────────────────────────────────┘

Citizen              Frontend           Backend            Database
   │                    │                  │                  │
   │── Register ───────→│                  │                  │
   │  (email, password)  │                  │                  │
   │                     │─ POST /auth/register              │
   │                     │─ {email, password} ──────────────→│
   │                     │                  │                  │
   │                     │                  │─ Hash password   │
   │                     │                  │  with bcrypt     │
   │                     │                  │─ Create User ───→│
   │                     │                  │                  │
   │                     │← HTTP 201 Created←────────────────│
   │                     │  {user_id, email} │                 │
   │← Show Success ──────│                  │                  │


┌─────────────────────────────────────────────────────────────┐
│                  LOGIN & TOKEN FLOW                         │
└─────────────────────────────────────────────────────────────┘

Citizen              Frontend           Backend            Database
   │                    │                  │                  │
   │── Login ───────────│                  │                  │
   │ (email, password)   │                  │                  │
   │                     │─ POST /auth/token                  │
   │                     │─ OAuth2 form ──────────────────────→│
   │                     │                  │                  │
   │                     │                  │─ Query User ────→│
   │                     │                  │← User + hash ←──│
   │                     │                  │                  │
   │                     │                  │─ Verify bcrypt  │
   │                     │                  │  (password hash) │
   │                     │                  │                  │
   │                     │← HTTP 200 ←─────│                  │
   │                     │ {access_token,   │                  │
   │                     │  refresh_token}  │                  │
   │                     │                  │                  │
   │← Store tokens ──────│                  │                  │
   │  (localStorage)     │                  │                  │


ACCESS TOKEN PAYLOAD (JWT):
{
  "sub": "user-uuid",        ← User ID (not email)
  "role": "citizen",         ← Role name at issuance time
  "type": "access",          ← Token type
  "exp": 1696XXX000,         ← Expiry (15 min)
  "iat": 1696XXX000          ← Issued time
}

REFRESH TOKEN PAYLOAD (JWT):
{
  "sub": "user-uuid",
  "type": "refresh",
  "exp": 1696YYY000,         ← Expiry (7 days)
  "iat": 1696XXX000
}


┌─────────────────────────────────────────────────────────────┐
│        PROTECTED REQUEST (WITH ACCESS TOKEN)                │
└─────────────────────────────────────────────────────────────┘

Citizen Browser          Frontend           Backend            Database
   │                       │                  │                  │
   │── GET /dashboard ─────│                  │                  │
   │                       │─ GET /api/v1/applications/me      │
   │                       │ (Authorization: Bearer access_token)
   │                       │──────────────────→│                 │
   │                       │                  │─ Verify JWT    │
   │                       │                  │  (signature,    │
   │                       │                  │   expiry,       │
   │                       │                  │   type)         │
   │                       │                  │                 │
   │                       │                  │─ Get User ─────→│
   │                       │                  │← User + role ←─│
   │                       │                  │                 │
   │                       │                  │─ Get Apps ─────→│
   │                       │                  │← User's apps ←─│
   │                       │                  │                 │
   │                       │← HTTP 200 ←─────│                 │
   │                       │ [{app1}, {app2}] │                 │
   │← Render dashboard ────│                  │                 │


TOKEN REJECTION FLOW:
- Expired token → HTTP 401 Unauthorized
- Invalid signature → HTTP 401 Unauthorized
- Missing token → HTTP 403 Forbidden
- Disabled user → HTTP 401 Unauthorized (DB recheck)
- Wrong role → HTTP 403 Forbidden (requires different role)
```

### 5.5 Database Schema (Entities & Relationships)

```
Role (Reference Table)
  id (PK)
  name (citizen | officer | admin)
  ├── created_at
  └── updated_at


User
  id (UUID, PK)
  email (Unique)
  password_hash (bcrypt)
  first_name
  last_name
  phone
  is_active
  role_id (FK → Role)
  ├── created_at
  ├── updated_at
  └── (1) ←─────────────── (*)
                          Application
                          AuditLog
                          Notification


Service (Catalog Table - Seeded)
  id (UUID, PK)
  code (business-registration)
  name (Business Registration)
  description
  category
  is_active
  ├── created_at
  ├── updated_at
  └── (1) ←─────────────── (*)
                          Application


ApplicationStatus (Reference Table - Seeded)
  id (UUID, PK)
  code (submitted, under_review, payment_pending, paid, officer_review, approved, rejected, completed)
  name (Display name)
  description
  ├── created_at
  └── updated_at


Application
  id (UUID, PK)
  user_id (FK → User) ─── Citizen who submitted
  service_id (FK → Service) ─ Which service (business-registration)
  status_id (FK → ApplicationStatus) ─ Current state
  form_data (JSON) ─── {"business_name": "...", "type": "...", ...}
  reference_number
  ├── created_at
  ├── updated_at
  └── (1) ←─────────────── (*)
                          Document
                          Payment
                          WorkflowTask
                          AuditLog


Document (Future Phase 5)
  id (UUID, PK)
  application_id (FK → Application)
  file_name
  file_path (encrypted storage)
  mime_type
  size_bytes
  is_verified
  virus_scan_status
  uploaded_by (FK → User)
  ├── created_at
  └── updated_at


Payment (Future Phase 9)
  id (UUID, PK)
  application_id (FK → Application)
  amount
  currency
  status (pending, completed, failed, refunded)
  payment_method (card, bank_transfer)
  transaction_id
  payment_date
  ├── created_at
  └── updated_at


WorkflowTask (Future Phase 6+)
  id (UUID, PK)
  application_id (FK → Application)
  assigned_to (FK → User) ─── Officer
  task_type (document_review, verification, approval)
  status (pending, completed, rejected)
  priority (low, medium, high)
  due_date
  ├── created_at
  ├── updated_at
  └── (1) ←─────────────── (*)
                          AuditLog


AuditLog (Append-only)
  id (UUID, PK)
  application_id (FK → Application)
  actor_id (FK → User) ─── Who made the change
  action (application_created, status_changed, document_uploaded, etc.)
  old_state (Previous status)
  new_state (New status)
  metadata (JSON) ─── {"ip": "...", "user_agent": "..."}
  ├── created_at
  └── (No updates - immutable)


Notification (Future Phase 7)
  id (UUID, PK)
  user_id (FK → User)
  type (email, sms)
  subject
  body
  status (pending, sent, failed)
  sent_at
  ├── created_at
  └── updated_at
```

---

## 6. Development Environment & Git Setup

### 6.1 Current Development Environment

**Tech Stack:**
- **Backend**: Python 3.13, FastAPI, SQLAlchemy, Alembic, Pydantic
- **Frontend**: Node.js 18+, Next.js 14, TypeScript, Tailwind CSS, React
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Infrastructure**: Docker Desktop, docker-compose

### 6.2 Repository Structure (Monorepo)

```
BizReg/
├── .git/                          ← Git version control
├── .gitignore                     ← Ignore patterns
├── docker-compose.yml             ← Local infrastructure
├── README.md                      ← Project introduction
│
├── backend/                       ← Python FastAPI API
│   ├── .env.example               ← Configuration template
│   ├── .env                       ← Local config (private, not committed)
│   ├── requirements.txt           ← Python dependencies
│   ├── alembic.ini               ← Migration config
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 20260827_0001_initial_schema.py
│   │   ├── env.py
│   │   └── script.py.mako
│   └── app/
│       ├── main.py               ← FastAPI app creation
│       ├── api/
│       │   ├── v1/router.py      ← Route collection
│       │   ├── v1/routes/        ← Feature routes
│       │   └── deps.py           ← Shared dependencies
│       ├── core/
│       │   ├── config.py         ← Settings/environment
│       │   └── security.py       ← Crypto utilities
│       ├── db/
│       │   ├── session.py        ← SQLAlchemy setup
│       │   └── base.py           ← ORM metadata
│       ├── models/               ← Domain models
│       ├── schemas/              ← Request/response schemas
│       └── services/             ← Business logic
│
├── frontend/                      ← Next.js React web app
│   ├── package.json              ← Node dependencies
│   ├── tsconfig.json             ← TypeScript config
│   ├── tailwind.config.ts        ← Styling config
│   ├── next.config.mjs           ← Next.js config
│   ├── app/
│   │   ├── layout.tsx            ← Root layout
│   │   ├── page.tsx              ← Landing page
│   │   ├── login/                ← Auth pages
│   │   ├── register/
│   │   ├── dashboard/
│   │   └── services/
│   ├── components/               ← Reusable components
│   └── lib/auth.ts               ← Auth utilities
│
└── docs/                          ← Study notes
    ├── 00-system-overview.md
    ├── 01-scaffolding.md
    ├── 02-data-modelling.md
    ├── 03-auth.md
    ├── 04-service-catalogue-and-application.md
    ├── architecture.md
    ├── frontend-layout.md
    └── api-reference.md
```

### 6.3 Git Configuration

**Initialize/Check Git:**
```powershell
# Check if git is initialized
git status

# If needed, initialize
git init

# Check current remote
git remote -v

# Add GitHub remote (if needed)
git remote add origin https://github.com/YOUR_USERNAME/BizReg.git
```

**Initial Commit (Phase 1):**
```powershell
# Add all files
git add .

# Commit
git commit -m "Phase 1: Project scaffolding and architecture

- Monorepo structure: frontend, backend, docs
- Next.js App Router web portal
- FastAPI REST API with versioning
- Docker Compose for PostgreSQL and Redis
- Study notes for each phase"

# Push to main branch
git push -u origin main
```

### 6.4 Local Development Setup Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ and npm installed
- [ ] Docker Desktop installed and running
- [ ] Repository cloned
- [ ] Backend:
  - [ ] `.env` file copied from `.env.example`
  - [ ] JWT_SECRET_KEY set to random value
  - [ ] Virtual environment created: `python -m venv .venv`
  - [ ] Dependencies installed: `pip install -r requirements.txt`
  - [ ] Docker containers running: `docker compose up -d`
  - [ ] Migrations applied: `alembic upgrade head`
  - [ ] API started: `uvicorn app.main:app --reload`
  - [ ] API available at: http://localhost:8000/docs
- [ ] Frontend:
  - [ ] Node modules installed: `npm install`
  - [ ] Dev server started: `npm run dev`
  - [ ] Frontend available at: http://localhost:3000

### 6.5 GitHub Project Setup

**Create Repository:**
1. Go to GitHub.com
2. Click "New repository"
3. Name: `BizReg`
4. Description: "Digital public-service platform for business registration"
5. Visibility: `Public` (for learning) or `Private` (for confidentiality)
6. Initialize with: README (we have one), .gitignore (important), no license yet

**Add to Local Repository:**
```powershell
git remote add origin https://github.com/YOUR_USERNAME/BizReg.git
git branch -M main
git push -u origin main
```

**Create Branches for Future Phases:**
```powershell
# Current work
git checkout -b phase-2-database

# After phase completion, merge
git checkout main
git merge phase-2-database
git push origin main
```

---

## 7. Success Criteria (Definition of Done)

### By End of Day 1

✅ **Understanding**
- [ ] Team understands what digital public-service platforms are
- [ ] Team can explain why Business Registration is the MVP
- [ ] Citizen-to-government workflow documented and reviewed
- [ ] Questions about requirements answered

✅ **Architecture**
- [ ] System architecture diagram reviewed and agreed
- [ ] Data flow understood (from citizen action to database)
- [ ] API layering understood (routes → services → models)
- [ ] Technology stack agreed

✅ **Environment**
- [ ] All team members have development environment working
- [ ] Backend runs on localhost:8000
- [ ] Frontend runs on localhost:3000
- [ ] Database is seeded and accessible
- [ ] Git repository initialized and pushed to GitHub

✅ **Deliverables**
- [ ] This document (Day 1 Analysis & Requirements)
- [ ] Repository with Phase 1 scaffolding committed
- [ ] Team can run the system locally
- [ ] API documentation accessible at /docs

---

## 8. Next Steps (Preview of Phases 2-4)

**Phase 2: Database & Data Modeling**
- Implement SQLAlchemy models
- Create Alembic migrations
- Seed reference data (roles, services, statuses)

**Phase 3: Authentication & Authorization**
- Implement user registration
- Implement OAuth2 password flow login
- JWT token generation and verification
- Role-Based Access Control (RBAC)

**Phase 4: Service Catalogue & Applications**
- Create service listing API
- Implement business registration form
- Store applications with form data
- Display applications on citizen dashboard
- Write audit logs

**Phase 5+: Advanced Features**
- Document upload and storage
- Payment integration
- Officer workflow and dashboard
- Notifications
- PDF certificates
- Security hardening
- Automated tests
- Production deployment

---

## Appendix A: API Reference (Current)

### Health Check
```
GET /api/v1/health
→ {"status": "ok"}
```

### Authentication (Phase 3)
```
POST /api/v1/auth/register
Request: {email, password, first_name, last_name, phone}
Response: {user_id, email, created_at}

POST /api/v1/auth/token
Request: {username: email, password}
Response: {access_token, refresh_token, token_type}

GET /api/v1/auth/me
Headers: Authorization: Bearer {access_token}
Response: {user_id, email, role, first_name, last_name}
```

### Services (Phase 4)
```
GET /api/v1/services
Response: [{id, code, name, description, category, is_active}]
```

### Applications (Phase 4)
```
POST /api/v1/applications
Headers: Authorization: Bearer {access_token}
Request: {service_id, form_data: {business_name, type, address, ...}}
Response: {id, user_id, service_id, status, form_data, created_at}

GET /api/v1/applications/me
Headers: Authorization: Bearer {access_token}
Response: [{id, service_id, status, form_data, created_at}]

GET /api/v1/applications/{id}
Headers: Authorization: Bearer {access_token}
Response: {id, user_id, service_id, status, form_data, created_at, audit_logs}
```

---

**Document Status**: Complete for Day 1  
**Last Updated**: 2026-08-28  
**Next Review**: End of Phase 2
