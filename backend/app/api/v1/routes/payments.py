"""Mock/sandbox payment endpoint (Day 8).

This implements the payment abstraction layer described in the curriculum.
During training, all payments use the "mock" provider, which always succeeds
after a simulated short delay. The abstraction means the route handler never
changes when a real gateway (MTN MoMo, Stripe, etc.) is integrated later.

Workflow integration:
  - Application must be in 'payment_pending' before a payment is initiated.
  - A successful mock payment transitions the application to 'paid'.
  - The transition is atomic and audited.
"""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_role
from app.db.session import get_db
from app.models.application import Application
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.payment import Payment
from app.models.user import User

router = APIRouter(prefix="/applications")

# Fixed registration fee for business registration (training constant).
REGISTRATION_FEE_RWF = Decimal("50000.00")


class InitiatePaymentRequest(BaseModel):
    """The provider field selects the backend; only 'mock' is accepted in training."""

    provider: str = Field(default="mock", pattern=r"^mock$")


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    provider: str
    provider_reference: str | None
    amount: Decimal
    currency: str
    status: str


def _load_application(db: Session, application_id: str, citizen: User) -> Application:
    application = db.scalar(
        select(Application)
        .options(joinedload(Application.citizen))
        .where(Application.id == application_id, Application.citizen_id == citizen.id)
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post(
    "/{application_id}/payment",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def initiate_payment(
    application_id: str,
    payload: InitiatePaymentRequest,
    current_user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """Initiate a registration-fee payment.

    For the mock provider, payment completes immediately and the application
    advances to 'paid'. In a real integration this endpoint would return a
    redirect URL and the confirmation would arrive via a webhook.
    """
    application = _load_application(db, application_id, current_user)

    if application.status_code != "payment_pending":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Payment can only be initiated when the application is in "
                f"'payment_pending' state; current state is '{application.status_code}'"
            ),
        )

    # Prevent duplicate payment records (the DB enforces uniqueness on application_id).
    existing = db.scalar(select(Payment).where(Payment.application_id == application_id))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A payment record already exists for this application",
        )

    # --- Mock provider: simulate an instant successful payment ---
    mock_reference = f"MOCK-{uuid.uuid4().hex[:12].upper()}"

    payment = Payment(
        application_id=application.id,
        provider="mock",
        provider_reference=mock_reference,
        amount=REGISTRATION_FEE_RWF,
        currency="RWF",
        status="completed",
    )
    db.add(payment)

    # Transition the application to 'paid'.
    old_status = application.status_code
    application.status_code = "paid"

    db.add(
        AuditLog(
            application=application,
            actor=current_user,
            action="payment_completed",
            from_state=old_status,
            to_state="paid",
            details={
                "provider": "mock",
                "reference": mock_reference,
                "amount": str(REGISTRATION_FEE_RWF),
                "currency": "RWF",
            },
        )
    )

    # Queue a payment confirmation notification.
    db.add(
        Notification(
            user=current_user,
            channel="email",
            recipient=current_user.email,
            subject="Payment confirmed — BizReg",
            body=(
                f"Dear {current_user.full_name},\n\n"
                f"Your payment of RWF {REGISTRATION_FEE_RWF:,.2f} has been received.\n"
                f"Reference: {mock_reference}\n\n"
                f"Your application is now under officer review.\n\n"
                f"The BizReg Team"
            ),
            delivery_status="queued",
        )
    )

    db.commit()
    db.refresh(payment)
    return PaymentResponse(
        id=payment.id,
        application_id=payment.application_id,
        provider=payment.provider,
        provider_reference=payment.provider_reference,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
    )


@router.get("/{application_id}/payment", response_model=PaymentResponse)
def get_payment(
    application_id: str,
    current_user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """Retrieve payment status for an application owned by the current citizen."""
    application = _load_application(db, application_id, current_user)
    payment = db.scalar(select(Payment).where(Payment.application_id == application.id))
    if payment is None:
        raise HTTPException(status_code=404, detail="No payment record found for this application")
    return PaymentResponse(
        id=payment.id,
        application_id=payment.application_id,
        provider=payment.provider,
        provider_reference=payment.provider_reference,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
    )
