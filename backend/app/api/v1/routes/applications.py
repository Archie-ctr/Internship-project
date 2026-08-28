"""Citizen-owned business-registration application endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_role
from app.db.session import get_db
from app.models.application import Application
from app.models.service import Service
from app.models.user import User
from app.schemas.application import (
    ApplicationDetailResponse,
    ApplicationResponse,
    CreateBusinessRegistrationRequest,
)
from app.services.application_service import create_business_registration

router = APIRouter(prefix="/applications")


def to_application_response(application: Application) -> ApplicationResponse:
    return ApplicationResponse(
        id=application.id,
        service_code=application.service.code,
        service_name=application.service.name,
        status=application.status_code,
        business_name=application.form_data["business_name"],
        created_at=application.created_at,
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: CreateBusinessRegistrationRequest,
    current_user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Create a citizen's application for the seeded Business Registration service."""
    service = db.scalar(
        select(Service).where(Service.code == "business-registration", Service.is_active.is_(True))
    )
    if service is None:
        raise HTTPException(status_code=503, detail="Business Registration is currently unavailable")
    application = create_business_registration(db, current_user, service, payload)
    # Refreshing relationships keeps the response mapping explicit and avoids
    # exposing the raw ORM object's internal fields.
    application = db.scalar(
        select(Application)
        .options(joinedload(Application.service))
        .where(Application.id == application.id)
    )
    assert application is not None
    return to_application_response(application)


@router.get("/me", response_model=list[ApplicationResponse])
def list_my_applications(
    current_user: User = Depends(require_role("citizen")), db: Session = Depends(get_db)
) -> list[ApplicationResponse]:
    """Only the owner can list their applications; no client-supplied user ID exists."""
    applications = db.scalars(
        select(Application)
        .options(joinedload(Application.service))
        .where(Application.citizen_id == current_user.id)
        .order_by(Application.created_at.desc())
    ).all()
    return [to_application_response(application) for application in applications]


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
def get_my_application(
    application_id: str,
    current_user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
) -> ApplicationDetailResponse:
    """Object-level authorisation prevents one citizen reading another's record."""
    application = db.scalar(
        select(Application)
        .options(joinedload(Application.service))
        .where(Application.id == application_id, Application.citizen_id == current_user.id)
    )
    if application is None:
        # A common response for absent and unauthorised IDs avoids revealing
        # whether another citizen has a particular application UUID.
        raise HTTPException(status_code=404, detail="Application not found")
    summary = to_application_response(application)
    return ApplicationDetailResponse(
        **summary.model_dump(), form_data=application.form_data, rejection_reason=application.rejection_reason
    )
