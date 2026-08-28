import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Uuid

from app.db.session import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.document import Document
    from app.models.payment import Payment
    from app.models.service import Service
    from app.models.user import User
    from app.models.workflow_task import WorkflowTask


class ApplicationStatus(Base):
    """Reference data for permitted workflow labels, seeded by the migration."""

    __tablename__ = "application_statuses"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    applications: Mapped[list["Application"]] = relationship(back_populates="status")


class Application(TimestampMixin, Base):
    """One citizen request for one public service.

    Structured form data remains JSON for Phase 2 because the form is introduced
    in Phase 4. Core ownership, service and status stay relational so the system
    can enforce them with foreign keys and query them efficiently.
    """

    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    citizen_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    status_code: Mapped[str] = mapped_column(
        ForeignKey("application_statuses.code"), nullable=False, default="submitted", index=True
    )
    form_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    registration_number: Mapped[str | None] = mapped_column(String(100), unique=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    citizen: Mapped["User"] = relationship(back_populates="applications")
    service: Mapped["Service"] = relationship(back_populates="applications")
    status: Mapped["ApplicationStatus"] = relationship(back_populates="applications")
    documents: Mapped[list["Document"]] = relationship(back_populates="application")
    payment: Mapped["Payment | None"] = relationship(back_populates="application")
    tasks: Mapped[list["WorkflowTask"]] = relationship(back_populates="application")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="application")
