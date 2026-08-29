# Day 3: Backend & REST APIs

**Date**: August 30, 2026  
**Duration**: 13 hours  
**Status**: ✅ Planned and ready for implementation

---

## 📋 Objectives

By the end of Day 3, you will have:

✅ Understood the FastAPI project structure used in the platform  
✅ Applied REST API principles to route design and naming  
✅ Created request/response schemas with Pydantic  
✅ Added validation and centralized error handling  
✅ Implemented service and application API endpoints  
✅ Tested endpoints with Swagger UI and local API requests  

---

## 🏗️ FastAPI Project Structure

This project uses a layered backend structure to keep the code organized and easy to extend:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Shared dependencies (DB, auth, role checks)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py         # Include all route modules
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── services.py
│   │           ├── applications.py
│   │           └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings and environment config
│   │   └── security.py          # Password hashing + JWT logic
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py              # SQLAlchemy Base import
│   │   └── session.py           # Engine and SessionLocal
│   ├── models/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── user.py
│   │   ├── service.py
│   │   ├── application.py
│   │   ├── role.py
│   │   ├── audit_log.py
│   │   ├── payment.py
│   │   ├── document.py
│   │   ├── notification.py
│   │   └── workflow_task.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── service.py
│   │   └── application.py
│   └── services/
│       ├── __init__.py
│       └── application_service.py
├── alembic/
│   ├── env.py
│   └── versions/
├── requirements.txt
├── alembic.ini
├── .env
└── README.md
```

### Why this structure matters

- `main.py` initializes the app and includes API routers.
- `api/v1/routes/` keeps endpoint logic separated by domain.
- `schemas/` defines validation for incoming and outgoing data.
- `services/` contains business logic instead of putting everything into routes.
- `models/` is strictly the database layer; routes do not directly manipulate DB objects in the endpoint layer.

---

## 🔄 REST Principles

REST (Representational State Transfer) is a set of rules for building HTTP APIs. This project follows the main ones.

### 1. Resource-based URLs

Use nouns for resources, not verbs:

```text
GET /api/v1/services
POST /api/v1/applications
GET /api/v1/applications/{id}
```

Bad example:

```text
GET /api/v1/get-services
POST /api/v1/create-application
```

### 2. Use HTTP methods correctly

| Method | Meaning | Example |
|--------|---------|---------|
| GET | Read resource | `GET /api/v1/services` |
| POST | Create resource | `POST /api/v1/applications` |
| PUT | Replace whole resource | `PUT /api/v1/applications/{id}` |
| PATCH | Partial update | `PATCH /api/v1/applications/{id}` |
| DELETE | Remove resource | `DELETE /api/v1/applications/{id}` |

### 3. Stateless communication

Each request should contain everything needed to process it:

- Authorization token in headers
- Request body with all required data
- No server-side session dependency for endpoint logic

### 4. JSON payloads

The API should work with JSON for both request and response bodies.

### 5. Use consistent status codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Resource created |
| 400 | Bad request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Conflict |
| 422 | Validation error |
| 500 | Internal server error |

### 6. Versioning

All routes use `/api/v1/...` to support future changes without breaking clients.

---

## 🧱 Request/Response Models with Pydantic

FastAPI uses Pydantic models to validate incoming data and shape responses.

### Example: Service schema

**File**: `backend/app/schemas/service.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ServiceBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceOut(ServiceBase):
    id: UUID
    is_active: bool

    class Config:
        orm_mode = True
```

### Example: Application schema

**File**: `backend/app/schemas/application.py`

```python
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from uuid import UUID

class ApplicationCreate(BaseModel):
    service_id: UUID
    form_data: Dict[str, Any] = Field(default_factory=dict)

class ApplicationOut(BaseModel):
    id: UUID
    user_id: UUID
    service_id: UUID
    status_id: UUID
    reference_number: str
    form_data: Dict[str, Any]

    class Config:
        orm_mode = True
```

### Why Pydantic models matter

- Validate request data before it reaches the database
- Convert data to clean Python types
- Return consistent response bodies
- Avoid repeating validation logic in routes

---

## ✅ Validation and Error Handling

Validation should happen at the API boundary. FastAPI automatically validates Pydantic models and returns `422` for invalid payloads.

### Example: Invalid input

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
```

If someone sends a short password or malformed email, FastAPI responds with:

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"min_length": 8}
    }
  ]
}
```

### Centralized error handling

Use `HTTPException` for expected problems:

```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )
```

### Recommended error patterns

```python
# Not found
raise HTTPException(status_code=404, detail="Service not found")

# Unauthorized
raise HTTPException(status_code=401, detail="Invalid credentials")

# Forbidden
raise HTTPException(status_code=403, detail="Insufficient permissions")

# Conflict
raise HTTPException(status_code=409, detail="User already exists")
```

### Best practice: return consistent structure

```python
{
  "detail": "User already exists"
}
```

Keep responses simple and consistent for frontend consumers.

---

## 📍 FastAPI Router Pattern

The app uses route modules and a central router include.

### `backend/app/api/v1/router.py`

```python
from fastapi import APIRouter
from app.api.v1.routes import auth, services, applications, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
```

### Application root entrypoint

**File**: `backend/app/main.py`

```python
from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(title="BizReg API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")
```

---

## 🔐 Service APIs

### Service catalogue endpoint

**File**: `backend/app/api/v1/routes/services.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.service import Service
from app.schemas.service import ServiceOut

router = APIRouter()

@router.get("", response_model=list[ServiceOut])
def list_services(db: Session = Depends(deps.get_db)):
    services = db.query(Service).filter(Service.is_active == True).all()
    return services
```

### API behavior

- `GET /api/v1/services`
- Returns all active services
- Public endpoint, no auth required
- Response is a list of service objects

### Example response

```json
[
  {
    "id": "3f9b0d9d-7f67-4a5c-9d3b-8c3d61f55c67",
    "code": "business-registration",
    "name": "Business Registration",
    "description": "Register a new business",
    "category": "Business",
    "is_active": true
  }
]
```

---

## 🧾 Application APIs

### Create application

**File**: `backend/app/api/v1/routes/applications.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.models.application import Application
from app.models.service import Service
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationOut
from app.services.application_service import create_business_registration

router = APIRouter()

@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    application = create_business_registration(
        db=db,
        user=current_user,
        service_id=payload.service_id,
        form_data=payload.form_data,
    )

    return application
```

### Get my applications

```python
@router.get("/me", response_model=list[ApplicationOut])
def get_my_applications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications
```

### Get application by ID

```python
@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view this application")

    return application
```

### Example response

```json
{
  "id": "92d34f66-6d2b-4dd5-8598-df7d26a24d32",
  "user_id": "a1c0fe80-3a75-447e-b5a0-c86c893c6d0f",
  "service_id": "3f9b0d9d-7f67-4a5c-9d3b-8c3d61f55c67",
  "status_id": "7b7b3b06-639f-4c5d-94b4-17071628f06d",
  "reference_number": "BR-20260830-283481",
  "form_data": {
    "business_name": "Kibra Foods Ltd",
    "business_type": "Sole proprietorship",
    "address": "Nairobi, Kenya"
  }
}
```

---

## 🧠 Business Logic Layer

The route layer should not contain too much logic. Put business workflows in `services/`.

### Example service function

**File**: `backend/app/services/application_service.py`

```python
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.application import Application
from app.models.audit_log import AuditLog


def create_business_registration(db: Session, user, service_id, form_data):
    ref_number = f"BR-{uuid4().hex[:8].upper()}"

    application = Application(
        user_id=user.id,
        service_id=service_id,
        status_id=user.role_id,
        form_data=form_data,
        reference_number=ref_number,
    )

    db.add(application)
    db.flush()

    audit = AuditLog(
        application_id=application.id,
        actor_id=user.id,
        action="application_created",
        old_state="new",
        new_state="submitted",
        metadata={"created_by": user.email},
    )

    db.add(audit)
    db.commit()
    db.refresh(application)
    return application
```

**Why this is good**:

- Route handles HTTP concerns only.
- Service handles core workflow logic.
- Audit log is created in the same transaction.
- Easier to test in isolation.

---

## 🛡️ Dependency Injection and Shared Auth

Shared logic is centralized in `backend/app/api/deps.py`.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = decode_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user
```

This pattern is powerful because the same dependency can be reused across all protected routes.

---

## 🧪 Validation Best Practices

### Recommended rules

- Validate all incoming request payloads with Pydantic
- Enforce minimum lengths and required fields
- Create separate models for input vs output
- Don’t trust client-side data
- Validate IDs, email formats, and date fields early

### Example validation patterns

```python
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
```

---

## ⚠️ Error Handling Patterns to Use

### 1. Validation errors

FastAPI automatically raises `422` for malformed payloads.

### 2. Domain errors

Use explicit `HTTPException` for application-specific logic:

```python
if service.is_active is False:
    raise HTTPException(
        status_code=400,
        detail="This service is temporarily unavailable",
    )
```

### 3. Unexpected exceptions

Use logging and return a generic 500 response in production.

```python
try:
    # risky workflow
except Exception as exc:
    logger.exception("Unexpected error while creating application")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 🧩 Response Model Strategy

Use response models to keep outputs consistent and avoid leaking internal database objects.

### Good response pattern

```python
@router.get("/services", response_model=list[ServiceOut])
```

This ensures that:

- only expected fields are returned
- JSON serialization is consistent
- the frontend receives a controlled shape

---

## ✅ Day 3 Deliverables

By the end of Day 3, deliver the following:

- [ ] FastAPI project structure understood and aligned with the repo
- [ ] REST route naming conventions applied consistently
- [ ] Pydantic request/response models created for services and applications
- [ ] Validation rules implemented for required fields and lengths
- [ ] Error handling added using `HTTPException`
- [ ] `GET /api/v1/services` implemented
- [ ] `POST /api/v1/applications` implemented
- [ ] `GET /api/v1/applications/me` implemented
- [ ] `GET /api/v1/applications/{id}` implemented
- [ ] Swagger docs tested at `/docs`

---

## 🧪 Testing Checklist

### API tests to run

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then test in browser or curl:

```bash
curl http://localhost:8000/api/v1/services
```

```bash
curl -X POST "http://localhost:8000/api/v1/applications" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "<uuid>",
    "form_data": {
      "business_name": "Kibra Foods Ltd",
      "business_type": "Sole proprietorship"
    }
  }'
```

### Validate in Swagger UI

Open:

```text
http://localhost:8000/docs
```

Check:

- route names appear as expected
- response models are shown
- validation failures return `422`
- auth-protected routes require tokens

---

## 📊 Success Criteria

Day 3 is complete when all of the following are true:

✅ FastAPI app loads without startup errors  
✅ `/api/v1/services` returns active services  
✅ `POST /api/v1/applications` creates an application record  
✅ `GET /api/v1/applications/me` shows only the current user's apps  
✅ `GET /api/v1/applications/{id}` enforces ownership checks  
✅ Validation rejects invalid payloads with `422`  
✅ Error messages are readable and consistent  
✅ Routes are cleanly separated into domain modules  
✅ Code is ready for frontend integration  

---

## 🔗 Next Phase

Once Day 3 is complete, continue to:

- **Day 4**: Service catalogue & application workflows
- **Day 5**: Frontend auth and protected routes
- **Day 6**: Business registration multistep form

---

## 📚 References

- FastAPI Docs: https://fastapi.tiangolo.com/
- Pydantic Docs: https://docs.pydantic.dev/
- REST API Design: https://restfulapi.net/
- OpenAPI Specification: https://swagger.io/specification/

