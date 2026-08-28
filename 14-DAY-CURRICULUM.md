# 14-Day Practical Curriculum: BizReg Platform Development

**Project**: Digital Public-Service Platform for Business Registration  
**Duration**: 14 days (2 weeks)  
**Framework**: FastAPI + Next.js + PostgreSQL  
**Start Date**: 2026-08-28  
**Repository**: https://github.com/Archie-ctr/Internship-project

---

## 📋 Curriculum Overview

| Week | Phase | Days | Focus | Status |
|------|-------|------|-------|--------|
| **Week 1** | Foundation | 1-7 | Problem definition, architecture, database, auth, services | 🔄 |
| **Week 2** | Implementation | 8-14 | Applications, workflow, documents, payments, deployment | 🔄 |

---

# 🎯 WEEK 1: FOUNDATION (Days 1-7)

## DAY 1: Problem, Requirements & Architecture ✅ COMPLETE

**Completed**: 2026-08-28

### Objectives
- [x] Understand digital public-service platforms
- [x] Select Business Registration as MVP service
- [x] Map citizen-to-government workflow (8 steps)
- [x] Define functional & non-functional requirements
- [x] Draw system architecture with 12 diagrams
- [x] Set up Git/GitHub with CI/CD pipelines

### Deliverables
- ✅ [DAY-1-ANALYSIS.md](docs/DAY-1-ANALYSIS.md) - 400+ line comprehensive analysis
- ✅ [ARCHITECTURE-DIAGRAMS.md](docs/ARCHITECTURE-DIAGRAMS.md) - 12 Mermaid diagrams
- ✅ [GITHUB-SETUP.md](GITHUB-SETUP.md) - Setup guide
- ✅ GitHub repository: https://github.com/Archie-ctr/Internship-project
- ✅ 5 GitHub Actions workflows configured
- ✅ Development environment ready

### Time Breakdown
- Understanding platforms: 1 hour
- Service selection & workflow mapping: 2 hours
- Requirements definition: 3 hours
- Architecture design & diagrams: 3 hours
- GitHub setup & CI/CD: 2 hours
- **Total**: 11 hours

### Key Links
- Documentation: [DAY-1-COMPLETE-SUMMARY.md](DAY-1-COMPLETE-SUMMARY.md)
- Repository: https://github.com/Archie-ctr/Internship-project
- Actions: https://github.com/Archie-ctr/Internship-project/actions

---

## DAY 2: Database Modeling & Schema Design

### Objectives
1. Implement all SQLAlchemy ORM models
2. Design relational schema with foreign keys
3. Create Alembic migration structure
4. Define model relationships and constraints
5. Add UUID primary keys and timestamps
6. Create model base classes and common fields

### Technical Tasks

#### Phase 2A: Model Base & Common Fields (2 hours)

**File**: `backend/app/models/common.py`
```python
# Implement:
├─ Base SQLAlchemy declarative base
├─ TimestampMixin (created_at, updated_at)
├─ UUIDMixin (id as UUID primary key)
├─ Combine into BaseModel
└─ Test imports in __init__.py
```

**Steps**:
1. Create base classes with sqlalchemy.orm
2. Define UUID primary key strategy
3. Add automatic timestamp handling
4. Test model inheritance

#### Phase 2B: Reference Models (1.5 hours)

**Files**: `backend/app/models/role.py`, `service.py`, `application.py` (status)

```python
# Role Model
├─ id: UUID (PK)
├─ name: Enum(citizen, officer, admin) UNIQUE
├─ description: String
└─ timestamps

# Service Model
├─ id: UUID (PK)
├─ code: String UNIQUE (business-registration)
├─ name: String
├─ description: Text
├─ category: String
├─ is_active: Boolean
└─ timestamps

# ApplicationStatus Model
├─ id: UUID (PK)
├─ code: Enum(submitted, under_review, ...)
├─ name: String
├─ description: Text
└─ timestamps
```

**Steps**:
1. Define enum classes for code values
2. Create models with Column definitions
3. Add __tablename__ and __repr__
4. Configure indexes on unique/code fields

#### Phase 2C: Domain Models (3 hours)

**Files**: `backend/app/models/user.py`, `application.py`, `audit_log.py`, etc.

```python
# User Model
├─ id: UUID (PK)
├─ email: String UNIQUE NOT NULL
├─ password_hash: String NOT NULL
├─ first_name, last_name: String
├─ phone: String
├─ is_active: Boolean DEFAULT True
├─ role_id: UUID (FK → Role)
├─ Relationship: role (Role)
└─ timestamps

# Application Model
├─ id: UUID (PK)
├─ user_id: UUID (FK → User) NOT NULL
├─ service_id: UUID (FK → Service) NOT NULL
├─ status_id: UUID (FK → ApplicationStatus) NOT NULL
├─ form_data: JSON (business_name, type, address, ...)
├─ reference_number: String UNIQUE
├─ Relationships: user, service, status, documents, payments, tasks, audits
└─ timestamps

# AuditLog Model (Append-only)
├─ id: UUID (PK)
├─ application_id: UUID (FK → Application)
├─ actor_id: UUID (FK → User)
├─ action: String (application_created, status_changed, ...)
├─ old_state: String
├─ new_state: String
├─ metadata: JSON (ip, user_agent, ...)
└─ created_at (no updates!)

# Document, Payment, WorkflowTask, Notification
├─ Similar structure with FK relationships
└─ Future-phase stub implementations
```

**Steps**:
1. Define each model in separate file
2. Create relationships with back_populates
3. Add cascade rules for foreign keys
4. Implement __repr__ for debugging
5. Export all models in __init__.py

#### Phase 2D: Alembic Migration (1.5 hours)

**Files**: `backend/alembic/env.py`, `versions/20260829_0001_initial_schema.py`

```python
# Generate migration
alembic revision --autogenerate -m "Initial schema with all tables"

# Generated migration should contain:
├─ CREATE TABLE operations for all 8 tables
├─ CREATE INDEX on unique columns
├─ CREATE FOREIGN KEY constraints
├─ SEQUENCE for auto-increment (if used)
└─ Seed INSERT statements for reference data
```

**Steps**:
1. Update SQLAlchemy models
2. Run alembic revision
3. Review generated migration
4. Verify DDL statements
5. Add seed data inserts
6. Test upgrade/downgrade

#### Phase 2E: Seed Data (1.5 hours)

**In migration file**:
```python
# Insert reference data:
├─ Roles: citizen, officer, admin
├─ Services: business-registration
├─ ApplicationStatus: submitted, under_review, payment_pending, paid, officer_review, approved, rejected, completed
└─ Timestamps for all
```

**Steps**:
1. Generate UUIDs for seed records
2. Create INSERT statements
3. Verify foreign key references
4. Test data loads correctly
5. Query and validate seed data

### Deliverables
- [ ] All 8 SQLAlchemy models implemented
- [ ] Model relationships defined with back_populates
- [ ] Alembic migration generated and tested
- [ ] Seed data in migration file
- [ ] Database schema validated
- [ ] `alembic upgrade head` runs successfully
- [ ] Seed data verifiable via PostgreSQL query
- [ ] Documentation updated in docs/02-data-modelling.md

### Testing Checklist
```bash
# Local testing
cd backend
python -c "from app.models import *; print('Models imported')"
docker compose up -d postgres
alembic upgrade head
docker compose exec postgres psql -U bizreg -d bizreg -c "SELECT * FROM roles;"
pytest tests/test_models.py  # If tests exist
```

### Time Breakdown
- Base models: 2 hours
- Reference models: 1.5 hours
- Domain models: 3 hours
- Alembic migration: 1.5 hours
- Seed data: 1.5 hours
- Testing & validation: 1.5 hours
- **Total**: 11 hours

### Success Criteria
- ✅ All models have UUID primary keys
- ✅ Foreign keys defined with ON DELETE CASCADE
- ✅ Unique constraints on email, service code, status code
- ✅ Timestamps automatic (created_at, updated_at)
- ✅ AuditLog is append-only (no update trigger)
- ✅ Migration file is clean and readable
- ✅ All seed data inserted
- ✅ GitHub Actions DB migration test passes

### Git Workflow
```bash
git checkout -b phase-2-database
# ... make changes ...
git add backend/app/models/ backend/alembic/
git commit -m "Phase 2: Database models and migrations

- Implement all 8 SQLAlchemy models
- Create base classes for common fields
- Define relationships and constraints
- Generate Alembic migration
- Add seed data for reference tables"
git push origin phase-2-database
# Create Pull Request on GitHub
# Wait for GitHub Actions to validate migration
# Merge when tests pass
```

### Phase Complete When
- [ ] All models compile without errors
- [ ] Migration runs: `alembic upgrade head`
- [ ] Seed data loads: 3 roles + 1 service + 8 statuses
- [ ] GitHub Actions DB workflow passes
- [ ] Merged to main branch

---

## DAY 3: Authentication & User Management

### Objectives
1. Implement password hashing (bcrypt)
2. Create user registration endpoint
3. Implement OAuth2 token generation (JWT)
4. Add JWT verification middleware
5. Implement role-based access control (RBAC)
6. Create `GET /auth/me` endpoint
7. Add token refresh mechanism

### Technical Tasks

#### Phase 3A: Security Utilities (1.5 hours)

**File**: `backend/app/core/security.py`

```python
# Implement:
├─ pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
├─ hash_password(password: str) → hashed_str
├─ verify_password(plain: str, hashed: str) → bool
├─ create_access_token(data: dict, expires_delta: Optional[timedelta])
├─ create_refresh_token(data: dict)
├─ decode_token(token: str, token_type: str) → dict
└─ handle JWT expiry and signature errors
```

**Steps**:
1. Import fastapi.security (OAuth2PasswordBearer)
2. Configure bcrypt with work factor
3. Implement token creation with expiry
4. Test password hashing and verification
5. Test token encode/decode

#### Phase 3B: Schemas for Authentication (1 hour)

**File**: `backend/app/schemas/auth.py`

```python
# Implement:
├─ UserRegisterRequest(email, password, first_name, last_name, phone)
├─ UserResponse(user_id, email, first_name, role)
├─ TokenResponse(access_token, refresh_token, token_type)
├─ TokenData(sub: UUID, role: str, type: str, iat: int, exp: int)
└─ Add validators: password length, email format
```

**Steps**:
1. Define Pydantic models
2. Add field validation
3. Test serialization/deserialization
4. Add to schemas/__init__.py

#### Phase 3C: Registration Endpoint (2 hours)

**File**: `backend/app/api/v1/routes/auth.py`

```python
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    req: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    # Steps:
    ├─ Validate email not already registered
    ├─ Hash password with bcrypt
    ├─ Get citizen role from database
    ├─ Create User record
    ├─ Commit transaction
    ├─ Return UserResponse (no password_hash!)
    └─ Handle errors: duplicate email, weak password
```

**Implementation**:
1. Query existing user by email
2. Hash password using security utility
3. Create User model instance
4. Commit to database
5. Return user data
6. Test with Postman/curl

#### Phase 3D: Login & Token Generation (2 hours)

**File**: `backend/app/api/v1/routes/auth.py`

```python
@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Steps:
    ├─ Query User by email (form_data.username)
    ├─ Verify password hash
    ├─ Load Role from database
    ├─ Create access token (15 min expiry) with sub=user_id, role=role.name
    ├─ Create refresh token (7 days expiry) with sub=user_id
    ├─ Return both tokens
    └─ Handle errors: user not found, invalid password
```

**Implementation**:
1. Use OAuth2PasswordRequestForm for form parsing
2. Query user by email
3. Use verify_password to check credentials
4. Load user's role
5. Call create_access_token and create_refresh_token
6. Return TokenResponse
7. Test login flow

#### Phase 3E: JWT Verification Dependencies (2 hours)

**File**: `backend/app/api/deps.py`

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Steps:
    ├─ Decode JWT token
    ├─ Verify token type is "access"
    ├─ Extract sub (user UUID)
    ├─ Query User from database
    ├─ Verify user is active
    ├─ Return User object
    └─ Handle errors: invalid token, user not found, user disabled

async def require_role(*allowed_roles: str):
    # Steps:
    ├─ Get current user (depends on get_current_user)
    ├─ Check user.role.name in allowed_roles
    ├─ Raise 403 Forbidden if not authorized
    └─ Return user or raise
```

**Implementation**:
1. Create dependency function
2. Parse JWT token
3. Verify signature and expiry
4. Query fresh user data from database
5. Check role authorization
6. Return user or raise HTTPException

#### Phase 3F: Get Current User Endpoint (1.5 hours)

**File**: `backend/app/api/v1/routes/auth.py`

```python
@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
):
    # Return current authenticated user
    return UserResponse.model_validate(current_user)
```

**Implementation**:
1. Use get_current_user dependency
2. Validate JWT and user status
3. Return user data
4. Test with Authorization header

#### Phase 3G: Role-Based Route Protection (1 hour)

**File**: `backend/app/api/v1/routes/applications.py`

```python
@router.post("/applications", status_code=201)
async def create_application(
    req: CreateApplicationRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("citizen")),  # RBAC check
    db: Session = Depends(get_db)
):
    # This endpoint is now protected
    # Only citizens can access
```

**Implementation**:
1. Add require_role dependency to each protected route
2. Test with wrong role returns 403
3. Test with valid role returns 200

### Deliverables
- [ ] Password hashing with bcrypt working
- [ ] `POST /auth/register` endpoint implemented
- [ ] `POST /auth/token` endpoint with JWT generation
- [ ] `GET /auth/me` endpoint returning current user
- [ ] JWT verification in all protected routes
- [ ] Role-based access control enforced
- [ ] Token expiry: access = 15 min, refresh = 7 days
- [ ] Error handling for auth failures
- [ ] Integration tests for auth flows
- [ ] Updated API documentation

### Testing Checklist
```bash
# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"MyPassword123","first_name":"John","last_name":"Doe","phone":"+1234567890"}'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=MyPassword123"

# Test get me
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Test invalid token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid_token"
# Should return 401
```

### Time Breakdown
- Security utilities: 1.5 hours
- Auth schemas: 1 hour
- Registration endpoint: 2 hours
- Login & token generation: 2 hours
- JWT verification: 2 hours
- Get me endpoint: 1.5 hours
- Role-based protection: 1 hour
- Testing & documentation: 2 hours
- **Total**: 13 hours

### Success Criteria
- ✅ Password never stored in plaintext
- ✅ Registration validates email format and password strength
- ✅ Login returns both access and refresh tokens
- ✅ Access token has 15-minute expiry
- ✅ Refresh token has 7-day expiry
- ✅ Token contains user UUID (not email)
- ✅ GET /auth/me re-verifies user status from database
- ✅ Role-protected routes return 403 for wrong role
- ✅ All token errors return appropriate HTTP status
- ✅ GitHub Actions passes all tests

### Git Workflow
```bash
git checkout -b phase-3-authentication
# ... implement auth ...
git add backend/app/core/security.py backend/app/schemas/auth.py backend/app/api/v1/routes/auth.py backend/app/api/deps.py
git commit -m "Phase 3: Authentication and authorization

- Implement password hashing with bcrypt
- Create user registration endpoint
- Implement OAuth2 password flow with JWT tokens
- Add JWT verification and role-based access control
- Endpoints: POST /register, POST /token, GET /me"
git push origin phase-3-authentication
```

### Phase Complete When
- [ ] Registration works with validation
- [ ] Login returns JWT tokens
- [ ] GET /auth/me returns current user
- [ ] Protected routes enforce role restrictions
- [ ] All GitHub Actions tests pass

---

## DAY 4: Service Catalogue & Application Management

### Objectives
1. Implement GET /services endpoint
2. Create business registration form schema
3. Implement POST /applications endpoint
4. Implement GET /applications/me endpoint
5. Create application service layer
6. Write audit logs for state changes
7. Validate service existence and citizen role

### Technical Tasks

#### Phase 4A: Service Schemas (1 hour)

**File**: `backend/app/schemas/service.py`

```python
# Implement:
├─ ServiceResponse(id, code, name, description, category, is_active)
└─ Pydantic model with validation
```

#### Phase 4B: Service Routes (1.5 hours)

**File**: `backend/app/api/v1/routes/services.py`

```python
@router.get("/services", response_model=List[ServiceResponse])
async def list_services(db: Session = Depends(get_db)):
    # Query all active services
    # Return list of ServiceResponse
    # No authentication required (public)
```

#### Phase 4C: Application Schemas (2 hours)

**File**: `backend/app/schemas/application.py`

```python
# Implement:
├─ CreateBusinessRegistrationRequest
│  ├─ service_id: UUID
│  ├─ form_data: dict with validated business info
│  │  ├─ business_name: String
│  │  ├─ business_type: Enum
│  │  ├─ address: String
│  │  ├─ business_activities: List[String]
│  │  └─ owner_details: dict
│  └─ validators for required fields
│
├─ ApplicationResponse
│  ├─ id: UUID
│  ├─ user_id: UUID
│  ├─ service_id: UUID
│  ├─ status: String
│  ├─ form_data: dict
│  ├─ reference_number: String
│  ├─ created_at: datetime
│  └─ updated_at: datetime
│
└─ ApplicationListResponse
   ├─ Similar to ApplicationResponse
   └─ For dashboard listing
```

#### Phase 4D: Application Service Layer (3 hours)

**File**: `backend/app/services/application_service.py`

```python
async def create_business_registration(
    user: User,
    service_id: UUID,
    form_data: dict,
    db: Session
) -> Application:
    # Steps:
    ├─ Verify user is citizen
    ├─ Query Service by ID
    ├─ Query ApplicationStatus "submitted"
    ├─ Generate reference number (e.g., BR-{timestamp}-{random})
    ├─ Create Application record in transaction
    │  ├─ user_id = user.id
    │  ├─ service_id = service.id
    │  ├─ status_id = submitted.id
    │  ├─ form_data = validated form data
    │  ├─ reference_number = generated
    │  └─ created_at = now()
    ├─ Create AuditLog record (same transaction)
    │  ├─ application_id = new app id
    │  ├─ actor_id = user.id
    │  ├─ action = "application_created"
    │  ├─ old_state = null
    │  ├─ new_state = "submitted"
    │  └─ metadata = {ip, user_agent, ...}
    ├─ Commit transaction (atomic)
    ├─ Return Application
    └─ Handle errors: service not found, invalid form data
```

**Implementation**:
1. Define service functions
2. Handle database transactions
3. Generate unique reference numbers
4. Write audit logs
5. Validate business rules
6. Return typed responses

#### Phase 4E: Create Application Endpoint (2 hours)

**File**: `backend/app/api/v1/routes/applications.py`

```python
@router.post("/applications", response_model=ApplicationResponse, status_code=201)
async def create_application(
    req: CreateBusinessRegistrationRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("citizen")),
    db: Session = Depends(get_db)
):
    # Call service function
    application = await create_business_registration(
        user=current_user,
        service_id=req.service_id,
        form_data=req.form_data,
        db=db
    )
    return ApplicationResponse.model_validate(application)
```

#### Phase 4F: List User Applications Endpoint (1.5 hours)

**File**: `backend/app/api/v1/routes/applications.py`

```python
@router.get("/applications/me", response_model=List[ApplicationListResponse])
async def list_user_applications(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("citizen")),
    db: Session = Depends(get_db)
):
    # Query applications where user_id = current_user.id
    # Order by created_at DESC
    # Return list of ApplicationResponse
    applications = db.query(Application).filter(
        Application.user_id == current_user.id
    ).order_by(Application.created_at.desc()).all()
    return [ApplicationListResponse.model_validate(app) for app in applications]
```

#### Phase 4G: Get Application Detail (1 hour)

**File**: `backend/app/api/v1/routes/applications.py`

```python
@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role("citizen")),
    db: Session = Depends(get_db)
):
    # Query application by ID
    # Verify current_user owns this application
    # Return ApplicationResponse
```

### Deliverables
- [ ] `GET /services` endpoint returns all active services
- [ ] `POST /applications` endpoint creates new application
- [ ] `GET /applications/me` endpoint lists user's applications
- [ ] `GET /applications/{id}` endpoint returns application details
- [ ] Application service layer with transaction management
- [ ] Audit logs written for application creation
- [ ] Form data validation with Pydantic
- [ ] Reference number generation and uniqueness
- [ ] User ownership validation (can only see own apps)
- [ ] Integration tests for all endpoints

### Testing Checklist
```bash
# List services
curl http://localhost:8000/api/v1/services

# Create application
curl -X POST http://localhost:8000/api/v1/applications \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "UUID",
    "form_data": {
      "business_name": "My Business",
      "business_type": "sole_proprietorship",
      "address": "123 Main St"
    }
  }'

# List user applications
curl http://localhost:8000/api/v1/applications/me \
  -H "Authorization: Bearer TOKEN"
```

### Time Breakdown
- Service schemas: 1 hour
- Service routes: 1.5 hours
- Application schemas: 2 hours
- Service layer: 3 hours
- Create endpoint: 2 hours
- List endpoint: 1.5 hours
- Detail endpoint: 1 hour
- Testing & documentation: 2 hours
- **Total**: 14 hours

### Success Criteria
- ✅ Services list returns all active services
- ✅ Citizens can submit applications
- ✅ Application data persisted with status "submitted"
- ✅ Audit log created for each submission
- ✅ Citizens see only their own applications
- ✅ Form data stored as JSON in database
- ✅ Reference number generated and unique
- ✅ All endpoints require authentication
- ✅ GitHub Actions tests pass

### Phase Complete When
- [ ] `GET /services` works
- [ ] `POST /applications` creates record
- [ ] `GET /applications/me` lists user apps
- [ ] Audit logs in database
- [ ] All tests passing

---

## DAY 5: Frontend Authentication Pages

### Objectives
1. Build registration page (`/register`)
2. Build login page (`/login`)
3. Implement client-side auth state management
4. Store JWT tokens in localStorage
5. Create protected route wrapper
6. Add logout functionality
7. Form validation and error handling

### Technical Tasks

#### Phase 5A: Auth Utility Functions (1.5 hours)

**File**: `frontend/lib/auth.ts`

```typescript
// Implement:
├─ getTokens(): { access_token?, refresh_token? }
├─ setTokens(access: string, refresh: string): void
├─ clearTokens(): void
├─ getAuthHeader(): { Authorization: string } | {}
├─ fetchWithAuth(url, options): Promise<Response>
└─ Test token storage/retrieval
```

#### Phase 5B: Registration Page (2 hours)

**File**: `frontend/app/register/page.tsx`

```typescript
// Implement:
├─ Form fields: email, password, firstName, lastName, phone
├─ Form validation
│  ├─ Email format
│  ├─ Password strength (12+ chars, mixed case, numbers)
│  ├─ Required fields
│  └─ Real-time error messages
├─ Submit handler
│  ├─ Call POST /api/v1/auth/register
│  ├─ Handle success: redirect to /login
│  └─ Handle errors: show validation messages
├─ Loading state during submission
├─ Error display
└─ Link to login page
```

**Implementation**:
1. Create form component with React hooks
2. Add form validation
3. Handle API calls
4. Manage loading/error states
5. Redirect after successful registration

#### Phase 5C: Login Page (2 hours)

**File**: `frontend/app/login/page.tsx`

```typescript
// Implement:
├─ Form fields: email, password
├─ Form validation (basic)
├─ Submit handler
│  ├─ Call POST /api/v1/auth/token
│  ├─ Store tokens: access_token, refresh_token
│  ├─ Redirect to /dashboard
│  └─ Handle auth errors (401)
├─ Loading state
├─ Error display
├─ Remember me (optional)
└─ Link to registration page
```

**Implementation**:
1. Form component with email/password fields
2. Handle token response
3. Store in localStorage
4. Redirect on success
5. Handle login errors

#### Phase 5D: Protected Route Wrapper (1.5 hours)

**File**: `frontend/components/ProtectedRoute.tsx`

```typescript
// Implement:
├─ Check if token exists in localStorage
├─ If no token:
│  ├─ Redirect to /login
│  └─ Show message "Please sign in"
├─ If token exists:
│  ├─ Render child component
│  └─ Load user data (GET /auth/me)
└─ Handle expired tokens
   ├─ Clear tokens
   └─ Redirect to login
```

**Implementation**:
1. useEffect to check auth status
2. useRouter to handle redirects
3. Load current user on mount
4. Show loading spinner while checking
5. Render protected content

#### Phase 5E: Logout Functionality (1 hour)

**File**: `frontend/components/SiteHeader.tsx`

```typescript
// Implement:
├─ Check if user is authenticated
├─ Show "Logout" button if logged in
├─ Logout handler
│  ├─ Clear tokens from localStorage
│  ├─ Clear any cached user data
│  ├─ Redirect to /login
│  └─ Show success message
└─ Show "Login/Register" links if not logged in
```

#### Phase 5F: Auth State Management (1 hour)

**File**: `frontend/lib/auth.ts` (enhanced)

```typescript
// Add:
├─ getCurrentUser(): Promise<User | null>
├─ isAuthenticated(): boolean
├─ getAccessToken(): string | null
└─ Handle token expiry gracefully
```

#### Phase 5G: Dashboard Page Structure (1.5 hours)

**File**: `frontend/app/dashboard/page.tsx`

```typescript
// Implement:
├─ Protected by ProtectedRoute
├─ Display user welcome message
├─ Show user's applications list (from GET /api/v1/applications/me)
│  ├─ Table/cards with application info
│  ├─ Status badge (submitted, under_review, etc.)
│  ├─ Created date
│  └─ Link to view details
├─ "New Application" button (link to /services)
└─ Logout button (in header)
```

### Deliverables
- [ ] `/register` page with form validation
- [ ] `/login` page with auth
- [ ] Tokens stored securely in localStorage
- [ ] Protected route wrapper component
- [ ] Logout functionality
- [ ] `/dashboard` page for authenticated users
- [ ] Error messages for failed auth
- [ ] Loading states during API calls
- [ ] Redirect to login if not authenticated
- [ ] User can see their applications on dashboard

### Testing Checklist
```bash
# 1. Navigate to http://localhost:3000/register
# 2. Fill form with valid data
# 3. Submit and verify redirect to login
# 4. Login with credentials
# 5. Verify tokens stored in localStorage
# 6. Navigate to /dashboard
# 7. Verify applications listed
# 8. Click logout
# 9. Verify redirect to login
```

### Time Breakdown
- Auth utilities: 1.5 hours
- Register page: 2 hours
- Login page: 2 hours
- Protected route: 1.5 hours
- Logout: 1 hour
- State management: 1 hour
- Dashboard page: 1.5 hours
- Testing & styling: 2 hours
- **Total**: 12.5 hours

### Success Criteria
- ✅ Registration form validates input
- ✅ Login returns tokens
- ✅ Tokens stored in localStorage
- ✅ Protected pages redirect to login
- ✅ Dashboard shows user's applications
- ✅ Logout clears tokens and redirects
- ✅ Forms handle errors gracefully
- ✅ Loading states show during API calls
- ✅ Responsive design works on mobile

### Phase Complete When
- [ ] Can register new user
- [ ] Can login and receive tokens
- [ ] Dashboard accessible after login
- [ ] Logout works correctly

---

## DAY 6: Business Registration Form & Application Flow

### Objectives
1. Create business registration form schema
2. Build business registration form page
3. Implement form validation
4. Add multi-step form layout
5. Integrate with POST /applications API
6. Show success message and redirect
7. Add form data preview before submission

### Technical Tasks

#### Phase 6A: Form Schema & Types (1 hour)

**File**: `frontend/app/services/business-registration/types.ts`

```typescript
// Define:
├─ BusinessRegistrationData interface
│  ├─ business_name: string
│  ├─ business_type: string (sole_proprietorship, partnership, corporation)
│  ├─ address: string
│  ├─ business_activities: string[]
│  ├─ owner_name: string
│  ├─ owner_email: string
│  └─ owner_phone: string
│
└─ FormStep enum: (BASIC, DETAILS, OWNER, REVIEW, SUBMIT)
```

#### Phase 6B: Multi-Step Form Component (3 hours)

**File**: `frontend/app/services/business-registration/page.tsx`

```typescript
// Implement:
├─ Step 1: Basic Information
│  ├─ Business name input
│  ├─ Business type dropdown
│  ├─ Address input
│  ├─ Validation: all required
│  └─ Next button
│
├─ Step 2: Business Details
│  ├─ Business activities (checkboxes)
│  ├─ Additional details (textarea)
│  └─ Back/Next buttons
│
├─ Step 3: Owner Information
│  ├─ Owner name
│  ├─ Owner email
│  ├─ Owner phone
│  ├─ Validation: email format
│  └─ Back/Next buttons
│
├─ Step 4: Review & Confirm
│  ├─ Display all entered data
│  ├─ Edit buttons for each section
│  ├─ Terms checkbox
│  └─ Submit/Back buttons
│
└─ Step 5: Success
   ├─ Show reference number
   ├─ Show next steps
   ├─ Redirect to dashboard (5 sec)
   └─ Manual "Go to Dashboard" button
```

#### Phase 6C: Form Validation (1.5 hours)

```typescript
// Implement:
├─ Client-side validation
│  ├─ Required fields
│  ├─ Email format
│  ├─ Phone format
│  └─ Min length for text fields
├─ Error messages
│  ├─ Per-field error display
│  └─ Form-level error handling
└─ Prevent submission if invalid
```

#### Phase 6D: API Integration (1.5 hours)

```typescript
// Implement:
├─ POST request to /api/v1/applications
├─ Include authorization header
├─ Send form data as JSON
├─ Handle response: application ID + reference number
├─ Handle errors: validation errors, server errors
└─ Show loading spinner during submission
```

#### Phase 6E: Styling & UX (2 hours)

```typescript
// Implement:
├─ Tailwind CSS styling
├─ Progress indicator (step X of 5)
├─ Form field styling
├─ Error message styling
├─ Success page styling
├─ Responsive design (mobile-first)
└─ Accessibility (labels, ARIA)
```

### Deliverables
- [ ] Business registration form with 4 steps
- [ ] Step-by-step validation
- [ ] Form data review before submission
- [ ] API integration with error handling
- [ ] Success page with reference number
- [ ] Auto-redirect to dashboard after success
- [ ] Responsive design for all devices
- [ ] Loading states during submission
- [ ] Error messages for invalid input

### Testing Checklist
```
1. Navigate to /services/business-registration
2. Fill out Step 1: business info
3. Verify validation errors for missing fields
4. Complete all 4 steps
5. Review page shows all entered data
6. Submit form
7. Verify POST /applications succeeds
8. See success page with reference number
9. Auto-redirect to dashboard or click button
10. Verify application appears on dashboard
```

### Time Breakdown
- Form types: 1 hour
- Multi-step form: 3 hours
- Validation: 1.5 hours
- API integration: 1.5 hours
- Styling & UX: 2 hours
- Testing & refinement: 1.5 hours
- **Total**: 11 hours

### Success Criteria
- ✅ Form validates all steps
- ✅ Data persists across steps
- ✅ Review page shows all data
- ✅ Submit creates application in database
- ✅ Reference number displayed
- ✅ Application appears on dashboard
- ✅ Responsive on mobile/tablet
- ✅ Error handling works

### Phase Complete When
- [ ] Can submit complete form
- [ ] Application created in database
- [ ] Dashboard shows new application

---

## DAY 7: API Testing & Documentation

### Objectives
1. Write integration tests for backend
2. Write unit tests for services
3. Create comprehensive API documentation
4. Add Postman collection
5. Test all endpoints end-to-end
6. Document error codes and responses
7. Performance testing

### Technical Tasks

#### Phase 7A: Backend Unit Tests (3 hours)

**Files**: `backend/tests/test_*.py`

```python
# Test coverage:
├─ test_auth.py
│  ├─ test_register_success
│  ├─ test_register_duplicate_email
│  ├─ test_login_success
│  ├─ test_login_invalid_password
│  ├─ test_get_me
│  └─ test_expired_token
│
├─ test_applications.py
│  ├─ test_create_application_success
│  ├─ test_create_app_only_citizen
│  ├─ test_list_user_applications
│  ├─ test_list_other_user_apps_forbidden
│  └─ test_audit_log_created
│
├─ test_services.py
│  ├─ test_list_services
│  ├─ test_service_returned_active_only
│  └─ test_list_requires_no_auth
│
└─ test_models.py
   ├─ test_user_model
   ├─ test_application_model
   ├─ test_audit_log_model
   └─ test_relationships
```

#### Phase 7B: Integration Tests (2 hours)

```python
# Test end-to-end flows:
├─ test_register_login_create_app_flow.py
│  ├─ User registers
│  ├─ User logs in
│  ├─ User creates application
│  ├─ User views application on dashboard
│  └─ Audit trail recorded
│
└─ test_rbac.py
   ├─ Officer cannot submit application
   ├─ Officer can view officer endpoints
   └─ Admin can do both
```

#### Phase 7C: Test Fixtures & Database Setup (1.5 hours)

```python
# Create:
├─ conftest.py with fixtures
│  ├─ Test database session
│  ├─ Test client (TestClient)
│  ├─ Test user (registered citizen)
│  ├─ Test service (business registration)
│  └─ Test application
│
└─ Mock data generators
```

#### Phase 7D: API Documentation Update (2 hours)

**File**: `docs/api-reference.md`

```markdown
# Updated sections:
├─ All endpoints with examples
├─ Request/response schemas
├─ Error codes and meanings
├─ Authentication examples
├─ Rate limiting (if added)
├─ Pagination (if added)
└─ Timestamps and timezones
```

#### Phase 7E: Postman Collection (1.5 hours)

**File**: `postman/BizReg.postman_collection.json`

```json
{
  "info": {
    "name": "BizReg API",
    "description": "Digital public-service platform"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        { "name": "Register", "request": {...} },
        { "name": "Login", "request": {...} },
        { "name": "Get Me", "request": {...} }
      ]
    },
    {
      "name": "Applications",
      "item": [...]
    },
    {
      "name": "Services",
      "item": [...]
    }
  ]
}
```

#### Phase 7F: Performance Testing (1.5 hours)

```python
# Test:
├─ GET /services: < 100ms
├─ POST /applications: < 500ms
├─ GET /applications/me: < 200ms
├─ Database query optimization
└─ N+1 query detection
```

### Deliverables
- [ ] Unit tests for all models and services
- [ ] Integration tests for all flows
- [ ] Test fixtures and test data
- [ ] 80%+ code coverage
- [ ] Comprehensive API documentation
- [ ] Postman collection for manual testing
- [ ] Performance benchmarks
- [ ] All tests passing (GitHub Actions)
- [ ] Test running guides in README

### Testing Checklist
```bash
# Run all tests
pytest --cov=app

# Run specific test
pytest tests/test_auth.py::test_register_success -v

# Generate coverage report
pytest --cov=app --cov-report=html

# Performance test
pytest tests/test_performance.py
```

### Time Breakdown
- Unit tests: 3 hours
- Integration tests: 2 hours
- Test fixtures: 1.5 hours
- API documentation: 2 hours
- Postman collection: 1.5 hours
- Performance testing: 1.5 hours
- Testing & refinement: 1.5 hours
- **Total**: 13.5 hours

### Success Criteria
- ✅ All critical paths tested
- ✅ 80%+ code coverage
- ✅ All tests passing
- ✅ API documented
- ✅ Postman collection works
- ✅ Performance acceptable
- ✅ Error cases handled
- ✅ GitHub Actions CI passes

### Phase Complete When
- [ ] All tests passing
- [ ] Coverage > 80%
- [ ] API documented
- [ ] Postman collection works

---

## Summary of Week 1

**Completed Phases**:
- Phase 1: Problem & Architecture ✅
- Phase 2: Database Modeling
- Phase 3: Authentication
- Phase 4: Service Catalogue & Applications
- Phase 5: Frontend Authentication
- Phase 6: Business Registration Form
- Phase 7: Testing & Documentation

**Week 1 Time**: ~80 hours (11-14 hours/day)

**Deliverables by End of Week 1**:
- ✅ Complete database schema
- ✅ Fully authenticated backend
- ✅ Registration & login pages
- ✅ Business registration form (4-step)
- ✅ Application submission & tracking
- ✅ Comprehensive tests
- ✅ Full API documentation

---

# 🎯 WEEK 2: IMPLEMENTATION (Days 8-14)

## DAY 8: Document Management & File Upload

### Objectives
1. Implement file upload API
2. Create document storage (S3/local)
3. Add virus scanning
4. Implement document list endpoint
5. Add file size validation
6. Create document delete endpoint
7. Secure document downloads

### Key Tasks
- Create `POST /applications/{id}/documents` endpoint
- Implement file storage abstraction (S3/local)
- Add virus scanning integration
- Create `GET /applications/{id}/documents` endpoint
- Add file access control
- Implement `DELETE /documents/{id}` endpoint

### Deliverables
- [ ] File upload working with validation
- [ ] Document list showing uploaded files
- [ ] Virus scanning integration
- [ ] Secure file storage
- [ ] File size limits enforced
- [ ] Document metadata in database
- [ ] Frontend upload component

---

## DAY 9: Officer Dashboard & Workflow

### Objectives
1. Create officer-only routes
2. Build officer dashboard page
3. Implement application review interface
4. Add status transition logic
5. Create task assignment system
6. Build notification queue
7. Add officer comments/notes

### Key Tasks
- Create `GET /officer/applications` endpoint
- Implement application assignment
- Create `POST /applications/{id}/review` endpoint
- Add workflow state transitions
- Build officer frontend pages

### Deliverables
- [ ] Officer dashboard showing pending apps
- [ ] Application review interface
- [ ] Status transitions working
- [ ] Task assignments to officers
- [ ] Notes/comments on applications

---

## DAY 10: Payment Integration & Status Transitions

### Objectives
1. Integrate payment gateway (Stripe/PayPal)
2. Create payment tracking
3. Implement payment status updates
4. Add payment retry logic
5. Create payment webhooks
6. Build payment confirmation page
7. Add refund handling

### Key Tasks
- Create `POST /applications/{id}/payment` endpoint
- Handle payment webhook callbacks
- Update application status on payment
- Create payment history tracking

### Deliverables
- [ ] Payment processing working
- [ ] Payment status tracking
- [ ] Webhook integration tested
- [ ] Payment confirmation page
- [ ] Refund mechanism

---

## DAY 11: Notifications & Email

### Objectives
1. Integrate email service (SendGrid/AWS SES)
2. Create notification templates
3. Implement status change notifications
4. Add SMS notifications (optional)
5. Create notification preferences
6. Build notification history
7. Add retry mechanism for failed sends

### Key Tasks
- Implement notification queue
- Create email template system
- Send notifications on status change
- Track notification history

### Deliverables
- [ ] Emails send on application submission
- [ ] Status change notifications
- [ ] Notification history tracked
- [ ] Email templates working
- [ ] Retry mechanism for failures

---

## DAY 12: PDF Certificates & Exports

### Objectives
1. Create certificate template
2. Implement PDF generation
3. Add QR code to certificates
4. Create certificate download endpoint
5. Add certificate verification system
6. Implement application export (PDF)
7. Create audit report generation

### Key Tasks
- Implement PDF generation (reportlab/weasyprint)
- Create certificate template
- Add digital signatures to certificates
- Generate certificates on approval

### Deliverables
- [ ] Certificates generate on approval
- [ ] QR codes working
- [ ] Certificate verification working
- [ ] PDF download working
- [ ] Export functionality

---

## DAY 13: Security Hardening & Deployment

### Objectives
1. Add rate limiting
2. Implement CORS properly
3. Add security headers
4. Implement logging & monitoring
5. Add API key management
6. Create backup strategy
7. Prepare for production deployment

### Key Tasks
- Add rate limiting (Redis)
- Configure security headers
- Implement request logging
- Add error tracking (Sentry)
- Create database backups

### Deliverables
- [ ] Rate limiting working
- [ ] Security headers present
- [ ] Logging comprehensive
- [ ] Error tracking integrated
- [ ] Backups automated

---

## DAY 14: Production Deployment & Demo

### Objectives
1. Deploy to cloud (AWS/GCP/Heroku)
2. Set up CI/CD pipeline
3. Create deployment documentation
4. Run security audit
5. Performance testing on prod
6. Create user documentation
7. Conduct final demo

### Key Tasks
- Deploy Docker containers
- Set up monitoring & alerts
- Create runbooks for common issues
- Conduct load testing
- Prepare demo scenarios

### Deliverables
- [ ] Production deployment working
- [ ] CI/CD pipeline complete
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Demo ready

---

## Summary

### Total Hours
- Week 1: ~80 hours
- Week 2: ~80 hours
- **Total**: ~160 hours

### Technologies Used
- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: TypeScript, Next.js, Tailwind CSS
- DevOps: Docker, GitHub Actions, Cloud
- Testing: pytest, React Testing Library
- Integrations: Stripe, SendGrid, AWS S3

### Final Deliverables
- ✅ Complete business registration platform
- ✅ 100+ API endpoints
- ✅ 50+ frontend pages/components
- ✅ Full test suite (80%+ coverage)
- ✅ Production deployment
- ✅ Comprehensive documentation
- ✅ Live demo

---

## Getting Started with Day 2

### Preparation
1. Review [DAY-1-ANALYSIS.md](docs/DAY-1-ANALYSIS.md)
2. Review [ARCHITECTURE-DIAGRAMS.md](docs/ARCHITECTURE-DIAGRAMS.md)
3. Ensure local development environment running
4. Read [02-data-modelling.md](docs/02-data-modelling.md)

### First Steps for Day 2
```bash
# 1. Create feature branch
git checkout -b phase-2-database

# 2. Start implementing models
cd backend
# ... implement models ...

# 3. Generate migration
alembic revision --autogenerate -m "Initial schema"

# 4. Test
alembic upgrade head

# 5. Commit and push
git add .
git commit -m "Phase 2: Database modeling"
git push origin phase-2-database
```

---

## Success Checklist

### End of Day 1 ✅
- [x] Day 1 analysis complete
- [x] Architecture documented
- [x] CI/CD configured
- [x] Repository setup

### End of Week 1 (Day 7)
- [ ] Database fully implemented
- [ ] Authentication complete
- [ ] All endpoints tested
- [ ] Frontend ready

### End of Week 2 (Day 14)
- [ ] Full platform deployed
- [ ] All features working
- [ ] Security hardened
- [ ] Ready for production

---

**Document**: 14-Day Curriculum  
**Status**: Days 1-7 Outlined, Days 8-14 Planned  
**Last Updated**: 2026-08-28  
**Repository**: https://github.com/Archie-ctr/Internship-project
