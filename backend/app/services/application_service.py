"""Application use cases kept separate from HTTP request handling."""

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.audit_log import AuditLog
from app.models.service import Service
from app.models.user import User
from app.schemas.application import CreateBusinessRegistrationRequest


def create_business_registration(
    db: Session, citizen: User, service: Service, payload: CreateBusinessRegistrationRequest
) -> Application:
    """Persist a new application and its initial audit event atomically.

    The citizen cannot supply a status. The API always starts new applications
    at `submitted`, preventing a crafted client request from skipping review or
    payment states. The explicit workflow module takes ownership of later
    transitions in Phase 6.
    """
    application = Application(
        citizen=citizen,
        service=service,
        status_code="submitted",
        form_data=payload.model_dump(mode="json"),
    )
    db.add(application)
    db.flush()  # Assign the UUID before the related audit record is inserted.
    db.add(
        AuditLog(
            application=application,
            actor=citizen,
            action="application_created",
            from_state=None,
            to_state="submitted",
            details={"service_code": service.code},
        )
    )
    db.commit()
    db.refresh(application)
    return application
