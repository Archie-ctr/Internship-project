# Day 2: Database Modeling & SQLAlchemy Implementation

**Date**: August 29, 2026  
**Duration**: 11 hours  
**Status**: 🔄 In Progress

---

## 📋 Objectives

By end of Day 2, you will have:

✅ Implemented 8 SQLAlchemy models with proper inheritance  
✅ Defined all relationships and foreign keys  
✅ Created Alembic migration for initial schema  
✅ Seeded reference data (roles, services, statuses)  
✅ Tested database connectivity and schema  
✅ All changes committed and pushed to GitHub  

---

## 🏗️ Architecture Overview

### Database Schema (8 Tables)

```
┌─────────────────────────────────────────────────────────┐
│                     PostgreSQL 16                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌─────────────┐                  │
│  │  User (1)    │◄───┤  Role (0..n)│                  │
│  └──────────────┘    └─────────────┘                  │
│         │                                              │
│         │ (1)                                          │
│         ▼                                              │
│  ┌──────────────────┐  ┌──────────────┐               │
│  │ Application (n)  │──┤ Service (1)  │               │
│  │                  │  └──────────────┘               │
│  │ application_id   │  ┌─────────────────┐            │
│  │ user_id (FK)     │──┤ ApplicationStatus│            │
│  │ service_id (FK)  │  └─────────────────┘            │
│  │ status_id (FK)   │                                 │
│  │ form_data (JSON) │                                 │
│  │ reference_number │                                 │
│  └──────────────────┘                                 │
│         │                                              │
│    ┌────┴──────────────────────┐                      │
│    ▼                            ▼                      │
│  ┌──────────────┐  ┌────────────────────┐             │
│  │ AuditLog (n) │  │ Document (n)       │             │
│  │              │  │ Payment (n)        │             │
│  │ app_id (FK)  │  │ WorkflowTask (n)   │             │
│  │ actor_id (FK)│  │ Notification (n)   │             │
│  └──────────────┘  └────────────────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### File Structure

```
backend/
├── app/models/
│   ├── __init__.py              (export all models)
│   ├── common.py                (BaseModel, mixins)
│   ├── role.py                  (Role, ApplicationStatus)
│   ├── service.py               (Service)
│   ├── user.py                  (User)
│   ├── application.py           (Application)
│   ├── audit_log.py             (AuditLog - append-only)
│   ├── document.py              (Document - stub)
│   ├── payment.py               (Payment - stub)
│   ├── notification.py          (Notification - stub)
│   └── workflow_task.py         (WorkflowTask - stub)
├── alembic/
│   ├── env.py                   (configuration)
│   └── versions/
│       └── 20260829_0001_initial_schema.py
└── db/
    ├── base.py                  (import all models for migrations)
    └── session.py               (SessionLocal, engine)
```

---

## 🎯 Phase 2A: Base Models & Mixins (2 hours)

### Task 2A.1: Create common.py with Base Classes

**File**: `backend/app/models/common.py`

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

# Base class for all models
Base = declarative_base()

class BaseModel(Base):
    """Abstract base model with common fields."""
    __abstract__ = True
    
    # UUID primary key
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

class UUIDMixin:
    """Mixin for UUID primary key."""
    # Note: Already in BaseModel, but available for composition patterns
    pass

# Combined base for most models
class TimestampedModel(BaseModel, TimestampMixin):
    """Base model with UUID PK and timestamps."""
    __abstract__ = True
```

### Task 2A.2: Verify Model Imports

**File**: `backend/app/models/__init__.py`

```python
from .common import Base, BaseModel, TimestampMixin, TimestampedModel

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "TimestampedModel",
]
```

### Testing Checklist (2A)

- [ ] `common.py` created without errors
- [ ] UUID and timestamps imported correctly
- [ ] `python -c "from app.models.common import Base; print('✓ Base model imports OK')"` returns success
- [ ] No import circular dependency issues

**Time Estimate**: 30 minutes (setup + testing)

---

## 🎯 Phase 2B: Reference Models (1.5 hours)

### Task 2B.1: Create role.py

**File**: `backend/app/models/role.py`

```python
from enum import Enum
from sqlalchemy import Column, String, Enum as SQLEnum
from .common import TimestampedModel

class RoleEnum(str, Enum):
    """Enumeration of user roles."""
    CITIZEN = "citizen"
    OFFICER = "officer"
    ADMIN = "admin"

class Role(TimestampedModel):
    """User roles: citizen, officer, admin."""
    __tablename__ = "role"
    
    name = Column(
        SQLEnum(RoleEnum),
        unique=True,
        nullable=False,
        index=True,
    )
    description = Column(String(255))
    
    def __repr__(self) -> str:
        return f"<Role {self.name}>"

class ApplicationStatusEnum(str, Enum):
    """Enumeration of application workflow statuses."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    OFFICER_REVIEW = "officer_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class ApplicationStatus(TimestampedModel):
    """Application status in the workflow."""
    __tablename__ = "application_status"
    
    code = Column(
        SQLEnum(ApplicationStatusEnum),
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    
    def __repr__(self) -> str:
        return f"<ApplicationStatus {self.code}>"
```

### Task 2B.2: Create service.py

**File**: `backend/app/models/service.py`

```python
from sqlalchemy import Column, String, Text, Boolean
from .common import TimestampedModel

class Service(TimestampedModel):
    """Service catalogue entry."""
    __tablename__ = "service"
    
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Service {self.code}: {self.name}>"
```

### Task 2B.3: Update __init__.py

**File**: `backend/app/models/__init__.py`

```python
from .common import Base, BaseModel, TimestampMixin, TimestampedModel
from .role import Role, RoleEnum, ApplicationStatus, ApplicationStatusEnum
from .service import Service

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "TimestampedModel",
    "Role",
    "RoleEnum",
    "ApplicationStatus",
    "ApplicationStatusEnum",
    "Service",
]
```

### Testing Checklist (2B)

- [ ] `role.py` and `service.py` created without errors
- [ ] Enums defined correctly
- [ ] All models inherit from TimestampedModel
- [ ] `python -c "from app.models import Role, Service; print('✓ Reference models OK')"` succeeds
- [ ] Index and unique constraints defined

**Time Estimate**: 40 minutes

---

## 🎯 Phase 2C: Domain Models (3 hours)

### Task 2C.1: Create user.py

**File**: `backend/app/models/user.py`

```python
from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .common import TimestampedModel

class User(TimestampedModel):
    """User account (citizen or officer)."""
    __tablename__ = "user"
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign key to Role
    role_id = Column(
        "role_id",
        type_="UUID",
        ForeignKey("role.id", ondelete="RESTRICT"),
        nullable=False,
    )
    
    # Relationships
    role = relationship("Role", lazy="joined")
    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="actor",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
```

### Task 2C.2: Create application.py

**File**: `backend/app/models/application.py`

```python
from sqlalchemy import Column, String, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON as PGJSON
from .common import TimestampedModel

class Application(TimestampedModel):
    """Citizen application for a service."""
    __tablename__ = "application"
    
    # Foreign keys
    user_id = Column(
        "user_id",
        type_="UUID",
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_id = Column(
        "service_id",
        type_="UUID",
        ForeignKey("service.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status_id = Column(
        "status_id",
        type_="UUID",
        ForeignKey("application_status.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    
    # Business data
    form_data = Column(
        PGJSON,
        default=dict,
        nullable=False,
        comment="Stores service-specific form data as JSON",
    )
    reference_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # Relationships
    user = relationship("User", back_populates="applications")
    service = relationship("Service")
    status = relationship("ApplicationStatus")
    
    documents = relationship(
        "Document",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    payments = relationship(
        "Payment",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    workflow_tasks = relationship(
        "WorkflowTask",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    notifications = relationship(
        "Notification",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Application {self.reference_number}: {self.service_id}>"
```

### Task 2C.3: Create audit_log.py (Append-Only)

**File**: `backend/app/models/audit_log.py`

```python
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON as PGJSON
from .common import BaseModel

class AuditLog(BaseModel):
    """Immutable audit log - records all application state changes."""
    __tablename__ = "audit_log"
    
    # Timestamps - NO updates allowed
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Foreign keys
    application_id = Column(
        "application_id",
        type_="UUID",
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id = Column(
        "actor_id",
        type_="UUID",
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Action details
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="e.g., application_created, status_changed, document_uploaded",
    )
    old_state = Column(Text)
    new_state = Column(Text)
    metadata = Column(
        PGJSON,
        default=dict,
        nullable=False,
        comment="Additional context: ip, user_agent, etc.",
    )
    
    # Relationships
    application = relationship("Application", back_populates="audit_logs")
    actor = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.application_id}>"
```

### Task 2C.4: Create Stub Models (Document, Payment, etc.)

**File**: `backend/app/models/document.py`

```python
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .common import TimestampedModel

class Document(TimestampedModel):
    """Uploaded document for an application."""
    __tablename__ = "document"
    
    application_id = Column(
        "application_id",
        type_="UUID",
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    size_bytes = Column(Integer)
    is_verified = Column(Boolean, default=False)
    virus_scan_status = Column(String(50), default="pending")
    
    uploaded_by = Column(
        "uploaded_by",
        type_="UUID",
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    application = relationship("Application", back_populates="documents")
    
    def __repr__(self) -> str:
        return f"<Document {self.file_name}>"
```

**File**: `backend/app/models/payment.py`

```python
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .common import TimestampedModel

class Payment(TimestampedModel):
    """Payment for an application."""
    __tablename__ = "payment"
    
    application_id = Column(
        "application_id",
        type_="UUID",
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="KES")
    status = Column(String(50), default="pending", index=True)
    payment_method = Column(String(50))
    transaction_id = Column(String(100), unique=True)
    payment_date = Column(String(50))
    
    application = relationship("Application", back_populates="payments")
    
    def __repr__(self) -> str:
        return f"<Payment {self.id}: {self.amount} {self.status}>"
```

**File**: `backend/app/models/notification.py`

```python
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .common import TimestampedModel

class Notification(TimestampedModel):
    """Notification sent to user."""
    __tablename__ = "notification"
    
    user_id = Column(
        "user_id",
        type_="UUID",
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    application_id = Column(
        "application_id",
        type_="UUID",
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    type = Column(String(50), nullable=False, index=True)  # email, sms
    subject = Column(String(255))
    body = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)
    sent_at = Column(String(50))
    
    def __repr__(self) -> str:
        return f"<Notification {self.type}: {self.status}>"
```

**File**: `backend/app/models/workflow_task.py`

```python
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .common import TimestampedModel

class WorkflowTask(TimestampedModel):
    """Task in application workflow."""
    __tablename__ = "workflow_task"
    
    application_id = Column(
        "application_id",
        type_="UUID",
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_to = Column(
        "assigned_to",
        type_="UUID",
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    task_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)
    priority = Column(Integer, default=0)
    due_date = Column(String(50))
    
    application = relationship("Application", back_populates="workflow_tasks")
    
    def __repr__(self) -> str:
        return f"<WorkflowTask {self.task_type}: {self.status}>"
```

### Task 2C.5: Update __init__.py with All Models

**File**: `backend/app/models/__init__.py` (Complete)

```python
from .common import Base, BaseModel, TimestampMixin, TimestampedModel
from .role import Role, RoleEnum, ApplicationStatus, ApplicationStatusEnum
from .service import Service
from .user import User
from .application import Application
from .audit_log import AuditLog
from .document import Document
from .payment import Payment
from .notification import Notification
from .workflow_task import WorkflowTask

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "TimestampedModel",
    "Role",
    "RoleEnum",
    "ApplicationStatus",
    "ApplicationStatusEnum",
    "Service",
    "User",
    "Application",
    "AuditLog",
    "Document",
    "Payment",
    "Notification",
    "WorkflowTask",
]
```

### Testing Checklist (2C)

- [ ] All 8 model files created without syntax errors
- [ ] Foreign keys defined with proper ondelete rules
- [ ] Relationships defined with back_populates
- [ ] `python -c "from app import models; print([m.__name__ for m in [models.User, models.Application, models.AuditLog]])"` succeeds
- [ ] No circular import issues
- [ ] __repr__ methods work for debugging

**Time Estimate**: 2 hours

---

## 🎯 Phase 2D: Alembic Migration (1.5 hours)

### Task 2D.1: Update db/base.py for Alembic

**File**: `backend/app/db/base.py`

```python
"""Import all models for Alembic migration discovery."""
from app.models.common import Base  # noqa: F401
from app.models.role import Role, ApplicationStatus  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.workflow_task import WorkflowTask  # noqa: F401

__all__ = [
    "Base",
    "Role",
    "ApplicationStatus",
    "Service",
    "User",
    "Application",
    "AuditLog",
    "Document",
    "Payment",
    "Notification",
    "WorkflowTask",
]
```

### Task 2D.2: Update alembic/env.py

**File**: `backend/alembic/env.py`

Verify or update:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import Base from app.db.base
from app.db.base import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# ... rest of env.py configuration
```

### Task 2D.3: Generate Migration

```bash
cd backend
alembic revision --autogenerate -m "Initial schema with all tables"
```

This creates: `backend/alembic/versions/20260829_HHMM_initial_schema.py`

### Task 2D.4: Verify Migration SQL

Open the generated migration file and verify:

```python
def upgrade() -> None:
    # Create Role table
    op.create_table('role',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.Enum('citizen', 'officer', 'admin', name='roleenum'), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create other tables...
    # Verify foreign key constraints
    # Verify indexes on unique columns

def downgrade() -> None:
    op.drop_table('audit_log')  # Must drop in reverse order
    op.drop_table('notification')
    # ... etc
```

### Task 2D.5: Test Migration

```bash
# Upgrade
alembic upgrade head

# Verify schema created
psql -U postgres -d bizreg -c "\dt"  # List tables
psql -U postgres -d bizreg -c "\d user"  # Describe table

# Downgrade
alembic downgrade base

# Upgrade again
alembic upgrade head
```

### Testing Checklist (2D)

- [ ] Migration file auto-generated successfully
- [ ] All 8 tables present in migration
- [ ] Foreign keys with correct ondelete actions
- [ ] Indexes on unique columns
- [ ] UUID type used correctly
- [ ] Upgrade executes without errors
- [ ] Downgrade executes without errors
- [ ] Schema matches models

**Time Estimate**: 50 minutes

---

## 🎯 Phase 2E: Seed Reference Data (1.5 hours)

### Task 2E.1: Add Seed Data to Migration

**In migration file** at end of `upgrade()` function:

```python
def upgrade() -> None:
    # ... existing table creation code ...
    
    # Seed reference data
    op.execute("""
        INSERT INTO role (id, name, description, created_at, updated_at) VALUES
        ('550e8400-e29b-41d4-a716-446655440001'::uuid, 'citizen', 'Service requester', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440002'::uuid, 'officer', 'Service processor', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440003'::uuid, 'admin', 'System administrator', NOW(), NOW());
    """)
    
    op.execute("""
        INSERT INTO application_status (id, code, name, description, created_at, updated_at) VALUES
        ('550e8400-e29b-41d4-a716-446655440101'::uuid, 'submitted', 'Application Submitted', 'Initial submission by citizen', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440102'::uuid, 'under_review', 'Under Review', 'Officer reviewing application', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440103'::uuid, 'payment_pending', 'Payment Pending', 'Awaiting payment', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440104'::uuid, 'paid', 'Payment Received', 'Payment confirmed', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440105'::uuid, 'officer_review', 'Officer Review', 'Officer final review', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440106'::uuid, 'approved', 'Approved', 'Application approved', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440107'::uuid, 'rejected', 'Rejected', 'Application rejected', NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440108'::uuid, 'completed', 'Completed', 'Service delivery completed', NOW(), NOW());
    """)
    
    op.execute("""
        INSERT INTO service (id, code, name, description, category, is_active, created_at, updated_at) VALUES
        ('550e8400-e29b-41d4-a716-446655440201'::uuid, 'business-registration', 'Business Registration', 'Register a new business', 'Business', true, NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440202'::uuid, 'license-renewal', 'License Renewal', 'Renew business license', 'Business', false, NOW(), NOW()),
        ('550e8400-e29b-41d4-a716-446655440203'::uuid, 'permit-application', 'Permit Application', 'Apply for trading permit', 'Business', false, NOW(), NOW());
    """)
```

### Task 2E.2: Test Seed Data

```bash
# Apply migration (includes seed)
alembic upgrade head

# Verify data
psql -U postgres -d bizreg -c "SELECT * FROM role;"
psql -U postgres -d bizreg -c "SELECT * FROM application_status;"
psql -U postgres -d bizreg -c "SELECT * FROM service;"
```

### Testing Checklist (2E)

- [ ] Seed data inserted after migration
- [ ] 3 roles present (citizen, officer, admin)
- [ ] 8 application statuses present
- [ ] 3 services present (1 active: business-registration)
- [ ] Downgrade preserves seed data (or clear on downgrade)
- [ ] UUIDs are valid format
- [ ] Timestamps are correct

**Time Estimate**: 40 minutes

---

## ✅ Day 2 Testing Checklist

### Model Implementation

- [ ] All 8 models created in separate files
- [ ] BaseModel and TimestampMixin working
- [ ] Foreign key relationships defined
- [ ] Cascade rules applied correctly
- [ ] Enums for Role and ApplicationStatus
- [ ] AuditLog is append-only (no updated_at)
- [ ] `python -m pytest tests/models/ -v` passes (if tests exist)

### Database Migration

- [ ] `alembic revision` generates valid migration
- [ ] All 8 tables created
- [ ] Foreign keys with correct actions
- [ ] Indexes on unique columns
- [ ] UUID primary keys used
- [ ] `alembic upgrade head` succeeds
- [ ] `alembic downgrade base` succeeds
- [ ] Schema verified: `\dt` and `\d role`

### Seed Data

- [ ] 3 roles inserted
- [ ] 8 application statuses inserted
- [ ] 3 services inserted (1 active)
- [ ] Data persists after upgrade/downgrade cycle
- [ ] Query data: `SELECT * FROM role;` returns 3 rows

### Code Quality

- [ ] No import errors
- [ ] No circular dependencies
- [ ] __repr__ methods work
- [ ] Type hints present
- [ ] Docstrings present
- [ ] No linting errors: `black`, `isort`, `flake8`

### Git Workflow

- [ ] Feature branch: `git checkout -b phase-2-database`
- [ ] All model files added
- [ ] Migration file added
- [ ] Commit: `git commit -m "Phase 2A-E: Database modeling and migrations"`
- [ ] Push: `git push origin phase-2-database`
- [ ] Create Pull Request

---

## 🔗 Integration with Existing Code

### Update backend/app/db/session.py

Ensure it imports from new models:

```python
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ... existing session configuration

# Verify engine and SessionLocal created correctly
```

### Database Connection String

From `backend/.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bizreg
```

---

## 📊 Success Criteria

By end of Phase 2E, you should have:

✅ **Code Deliverables**:
- All 8 SQLAlchemy models implemented
- Base classes with mixins
- Alembic migration working
- Seed data inserted

✅ **Verification**:
- `psql` shows 8 tables
- `\d role` shows correct columns
- Seed data queries return expected results

✅ **Git**:
- Phase branch created and pushed
- All changes committed
- Ready for code review

✅ **Time**:
- Completed in ~11 hours
- On track for Day 3 (Authentication)

---

## 🚀 Ready for Day 3?

Once Phase 2E completes:

1. Create Pull Request: `phase-2-database` → `main`
2. Review and merge
3. Switch to `main`: `git checkout main && git pull`
4. Start Day 3: Authentication & Authorization

**Next Phase**: Implement password hashing, user registration, JWT tokens, and RBAC.

---

## 📚 References

- **SQLAlchemy 2.0 Docs**: https://docs.sqlalchemy.org/
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **PostgreSQL UUID**: https://www.postgresql.org/docs/current/uuid-ossp.html
- **Project Docs**: See `docs/02-data-modelling.md`

