"""Officer and admin endpoints for the application review workflow.

State machine (Day 7):
  submitted → under_review → payment_pending → paid → officer_review
           → approved → completed
           → rejected  (at any review stage)

Officers can transition applications through all states after initial submission.
Admins have the same access plus user management (added in later phases).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_role
from app.db.session import get_db
from app.models.application import Application
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.user import User
from app.models.workflow_task import WorkflowTask
from app.schemas.officer import (
    ApplicationDetailOfficer,
    ApplicationListItem,
    AssignTaskRequest,
    ReviewDecisionRequest,
    StatusTransitionRequest,
    TaskResponse,
)

router = APIRouter(prefix="/officer")

# ── Valid state transitions the workflow engine allows ───────────────────────
# Each key is the current state; the value is the set of permitted next states.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "submitted": {"under_review", "rejected"},
    "under_review": {"payment_pending", "rejected"},
    "payment_pending": {"paid", "rejected"},
    "paid": {"officer_review", "rejected"},
    "officer_review": {"approved", "rejected"},
    "approved": {"completed"},
    "rejected": set(),
    "completed": set(),
}


def _to_list_item(application: Application) -> ApplicationListItem:
    return ApplicationListItem(
        id=application.id,
        service_code=application.service.code,
        service_name=application.service.name,
        citizen_email=application.citizen.email,
        status=application.status_code,
        business_name=application.form_data.get("business_name", ""),
        created_at=application.created_at,
    )


def _to_detail(application: Application) -> ApplicationDetailOfficer:
    return ApplicationDetailOfficer(
        id=application.id,
        service_code=application.service.code,
        service_name=application.service.name,
        citizen_email=application.citizen.email,
        status=application.status_code,
        business_name=application.form_data.get("business_name", ""),
        form_data=application.form_data,
        registration_number=application.registration_number,
        rejection_reason=application.rejection_reason,
        created_at=application.created_at,
    )


def _load_application(db: Session, application_id: str) -> Application:
    """Load an application with all needed relationships; raise 404 if absent."""
    application = db.scalar(
        select(Application)
        .options(
            joinedload(Application.service),
            joinedload(Application.citizen),
        )
        .where(Application.id == application_id)
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def _record_transition(
    db: Session,
    application: Application,
    actor: User,
    action: str,
    old_status: str,
    new_status: str,
    details: dict,
) -> None:
    """Append an audit log entry and queue a notification in one flush."""
    db.add(
        AuditLog(
            application=application,
            actor=actor,
            action=action,
            from_state=old_status,
            to_state=new_status,
            details=details,
        )
    )
    # Notification is queued here; a background worker delivers it (Day 8).
    db.add(
        Notification(
            user=application.citizen,
            channel="email",
            recipient=application.citizen.email,
            subject=f"Application update: {new_status.replace('_', ' ').title()}",
            body=(
                f"Dear {application.citizen.full_name},\n\n"
                f"Your business registration application status has changed to: "
                f"{new_status.replace('_', ' ').title()}.\n\n"
                f"Application ID: {application.id}\n\n"
                f"The BizReg Team"
            ),
            delivery_status="queued",
        )
    )


# ── Dashboard: list all pending/active applications ──────────────────────────

@router.get("/applications", response_model=list[ApplicationListItem])
def list_pending_applications(
    status_filter: str | None = None,
    current_officer: User = Depends(require_role("officer", "admin")),
    db: Session = Depends(get_db),
) -> list[ApplicationListItem]:
    """Return all applications, optionally filtered by status.

    Officers see every application so they can be assigned as reviewers.
    """
    query = select(Application).options(
        joinedload(Application.service),
        joinedload(Application.citizen),
    )
    if status_filter:
        query = query.where(Application.status_code == status_filter)
    query = query.order_by(Application.created_at.asc())
    applications = db.scalars(query).all()
    return [_to_list_item(app) for app in applications]


@router.get("/applications/{application_id}", response_model=ApplicationDetailOfficer)
def get_application_detail(
    application_id: str,
    current_officer: User = Depends(require_role("officer", "admin")),
    db: Session = Depends(get_db),
) -> ApplicationDetailOfficer:
    """Full detail of any application, including form data and history."""
    return _to_detail(_load_application(db, application_id))


# ── Status transitions ────────────────────────────────────────────────────────

@router.post("/applications/{application_id}/transition", response_model=ApplicationDetailOfficer)
def transition_status(
    application_id: str,
    payload: StatusTransitionRequest,
    current_officer: User = Depends(require_role("officer", "admin")),
    db: Session = Depends(get_db),
) -> ApplicationDetailOfficer:
    """Advance or reject an application following the allowed state machine.

    The server enforces the transition table so no crafted client request can
    skip states or reopen a closed application.
    """
    application = _load_application(db, application_id)
    old_status = application.status_code
    allowed = ALLOWED_TRANSITIONS.get(old_status, set())

    if payload.new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Cannot move from '{old_status}' to '{payload.new_status}'. "
                f"Allowed next states: {sorted(allowed) or 'none (terminal state)'}"
            ),
        )

    application.status_code = payload.new_status
    _record_transition(
        db,
        application,
        current_officer,
        "status_transitioned",
        old_status,
        payload.new_status,
        {"notes": payload.notes, "officer_id": str(current_officer.id)},
    )
    db.commit()
    db.refresh(application)
    return _to_detail(application)


@router.post("/applications/{application_id}/review", response_model=ApplicationDetailOfficer)
def review_application(
    application_id: str,
    payload: ReviewDecisionRequest,
    current_officer: User = Depends(require_role("officer", "admin")),
    db: Session = Depends(get_db),
) -> ApplicationDetailOfficer:
    """Approve or reject an application that is in 'officer_review' state.

    A rejection reason is required when the decision is 'rejected'.
    An approval auto-generates a registration number and moves the application
    to 'approved', ready for certificate generation.
    """
    application = _load_application(db, application_id)

    if application.status_code != "officer_review":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Review requires status 'officer_review'; current status is '{application.status_code}'",
        )

    if payload.decision == "rejected" and not payload.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A rejection reason is required when rejecting an application",
        )

    old_status = application.status_code
    application.status_code = payload.decision

    if payload.decision == "approved":
        # Generate a deterministic human-readable registration number.
        # A production system would use a sequential counter from a database
        # sequence; UUID suffixes are acceptable for learning purposes.
        application.registration_number = f"BR-{uuid.uuid4().hex[:8].upper()}"
        application.rejection_reason = None
    else:
        application.rejection_reason = payload.rejection_reason

    _record_transition(
        db,
        application,
        current_officer,
        f"application_{payload.decision}",
        old_status,
        payload.decision,
        {
            "officer_id": str(current_officer.id),
            "rejection_reason": payload.rejection_reason,
        },
    )
    db.commit()
    db.refresh(application)
    return _to_detail(application)


# ── Task assignment ───────────────────────────────────────────────────────────

@router.post("/applications/{application_id}/assign", response_model=TaskResponse)
def assign_application(
    application_id: str,
    payload: AssignTaskRequest,
    current_officer: User = Depends(require_role("officer", "admin")),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Assign an application to an officer by creating a workflow task.

    Only one open review task per application is enforced to keep the workflow
    simple during the learning phase.
    """
    application = _load_application(db, application_id)

    # Verify the target officer exists.
    assigned = db.scalar(select(User).where(User.id == payload.officer_id))
    if assigned is None:
        raise HTTPException(status_code=404, detail="Officer not found")
    if assigned.role.name not in ("officer", "admin"):
        raise HTTPException(status_code=422, detail="Target user is not an officer or admin")

    # Close any previous open task before creating a new assignment.
    existing = db.scalars(
        select(WorkflowTask)
        .where(WorkflowTask.application_id == application_id, WorkflowTask.status == "open")
    ).all()
    for task in existing:
        task.status = "reassigned"

    task = WorkflowTask(
        application=application,
        assigned_officer_id=payload.officer_id,
        task_type="review",
        status="open",
    )
    db.add(task)
    db.add(
        AuditLog(
            application=application,
            actor=current_officer,
            action="application_assigned",
            from_state=application.status_code,
            to_state=application.status_code,
            details={"assigned_to": str(payload.officer_id)},
        )
    )
    db.commit()
    db.refresh(task)
    return TaskResponse(
        id=task.id,
        application_id=task.application_id,
        task_type=task.task_type,
        status=task.status,
        notes=task.notes,
        created_at=task.created_at,
    )


# ── Audit trail ───────────────────────────────────────────────────────────────

@router.get("/applications/{application_id}/audit", response_model=list[dict])
def get_audit_trail(
    application_id: str,
    current_officer: User = Depends(require_role("officer", "admin")),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return the complete, immutable audit history for an application."""
    _load_application(db, application_id)  # Raises 404 if absent.
    logs = db.scalars(
        select(AuditLog)
        .where(AuditLog.application_id == application_id)
        .order_by(AuditLog.created_at.asc())
    ).all()
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "from_state": log.from_state,
            "to_state": log.to_state,
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


# ── Admin: list all platform users ───────────────────────────────────────────

from pydantic import BaseModel as _BaseModel, ConfigDict as _ConfigDict

class UserSummary(_BaseModel):
    model_config = _ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool


@router.get("/users", response_model=list[UserSummary])
def list_users(
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> list[UserSummary]:
    """Admin-only: list every platform user with their role."""
    users = db.scalars(
        select(User).options(joinedload(User.role)).order_by(User.email)
    ).all()
    return [
        UserSummary(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role.name,
            is_active=u.is_active,
        )
        for u in users
    ]
