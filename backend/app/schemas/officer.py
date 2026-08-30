"""Request/response schemas for officer and admin workflow operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationListItem(BaseModel):
    """Compact summary shown in the officer dashboard list view."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_code: str
    service_name: str
    citizen_email: str
    status: str
    business_name: str
    created_at: datetime


class ReviewDecisionRequest(BaseModel):
    """Body for approve / reject transitions."""

    decision: str = Field(pattern=r"^(approved|rejected)$")
    rejection_reason: str | None = Field(default=None, max_length=1000)


class StatusTransitionRequest(BaseModel):
    """Generic body for officer-driven state advances (e.g. under_review → payment_pending)."""

    new_status: str = Field(
        pattern=r"^(under_review|payment_pending|paid|officer_review|approved|rejected|completed)$"
    )
    notes: str | None = Field(default=None, max_length=1000)


class ApplicationDetailOfficer(BaseModel):
    """Full application detail visible to officers and admins."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_code: str
    service_name: str
    citizen_email: str
    status: str
    business_name: str
    form_data: dict
    registration_number: str | None
    rejection_reason: str | None
    created_at: datetime


class AssignTaskRequest(BaseModel):
    officer_id: UUID


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    task_type: str
    status: str
    notes: str | None
    created_at: datetime
