"""Seed rich default data for demos and development.

Run from the backend/ directory:
    python seed_default_data.py

Creates:
  - 5 citizen users
  - 8 applications spread across every workflow state
  - Payments for applications that are paid / approved / completed
  - Audit logs for every transition
  - Notifications for each status change
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import app.db.base  # noqa: F401 — registers all ORM relationships

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.application import Application
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.payment import Payment
from app.models.role import Role
from app.models.service import Service
from app.models.user import User
from app.models.workflow_task import WorkflowTask
from sqlalchemy import select

db = SessionLocal()

# ── helpers ──────────────────────────────────────────────────────────────────

def now(offset_days: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=offset_days)

def get_role(name: str) -> Role:
    r = db.scalar(select(Role).where(Role.name == name))
    assert r, f"Role '{name}' not found — run alembic upgrade head first"
    return r

def get_or_create_user(email: str, full_name: str, role_name: str, password: str) -> User:
    u = db.scalar(select(User).where(User.email == email))
    if u:
        return u
    u = User(email=email, full_name=full_name,
             password_hash=hash_password(password), role=get_role(role_name))
    db.add(u)
    db.flush()
    return u

def audit(app_obj: Application, actor: User, action: str,
          from_s: str | None, to_s: str, details: dict) -> None:
    db.add(AuditLog(application=app_obj, actor=actor,
                    action=action, from_state=from_s,
                    to_state=to_s, details=details))

def notify(user: User, subject: str, body: str, channel: str = "email",
           status: str = "delivered") -> None:
    db.add(Notification(user=user, channel=channel,
                        recipient=user.email, subject=subject,
                        body=body, delivery_status=status))

def make_app(citizen: User, service: Service, status_code: str,
             business_name: str, business_type: str,
             reg_number: str | None = None,
             rejection_reason: str | None = None) -> Application:
    a = Application(
        citizen=citizen, service=service, status_code=status_code,
        form_data={
            "business_name": business_name,
            "business_type": business_type,
            "owner": {"full_name": citizen.full_name,
                      "id_number": "1199880" + str(uuid.uuid4().int)[:7],
                      "phone_number": "+250788" + str(uuid.uuid4().int)[:6]},
            "address": {"line1": "KG 7 Ave", "city": "Kigali",
                        "district": "Gasabo", "country": "Rwanda"},
        },
        registration_number=reg_number,
        rejection_reason=rejection_reason,
    )
    db.add(a)
    db.flush()
    return a

# ── idempotency guard ─────────────────────────────────────────────────────────
existing_count = db.query(Application).count()
if existing_count >= 8:
    print(f"Already have {existing_count} applications — skipping seed. Delete rows to re-run.")
    db.close()
    exit(0)

# ── fetch shared objects ──────────────────────────────────────────────────────

biz_reg = db.scalar(select(Service).where(Service.code == "business-registration"))
assert biz_reg, "business-registration service not found"

officer  = get_or_create_user("officer@bizreg.rw",  "Bob Nkurunziza", "officer", "OfficerPass1234")
admin_u  = get_or_create_user("admin@bizreg.rw",    "Carol Mutesi",   "admin",   "AdminPass12345")

# ── citizen accounts ──────────────────────────────────────────────────────────

citizens = [
    get_or_create_user("alice@example.rw",   "Alice Uwimana",    "citizen", "CitizenPass1234"),
    get_or_create_user("jean@example.rw",    "Jean Paul Habimana","citizen", "CitizenPass1234"),
    get_or_create_user("grace@example.rw",   "Grace Murekatete", "citizen", "CitizenPass1234"),
    get_or_create_user("patrick@example.rw", "Patrick Mugisha",  "citizen", "CitizenPass1234"),
    get_or_create_user("diana@example.rw",   "Diana Ingabire",   "citizen", "CitizenPass1234"),
    get_or_create_user("citizen@bizreg.rw",  "Alice Uwimana",    "citizen", "CitizenPass1234"),
]
alice, jean, grace, patrick, diana, demo_citizen = citizens

# ── applications ──────────────────────────────────────────────────────────────

print("Creating applications…")

# 1. SUBMITTED — fresh, just arrived
a1 = make_app(alice, biz_reg, "submitted",
              "Kigali Tech Solutions Ltd", "limited_company")
audit(a1, alice, "application_created", None, "submitted",
      {"service_code": "business-registration"})
notify(alice, "Application received", f"Dear {alice.full_name}, your application for "
       f"Kigali Tech Solutions Ltd has been received. Reference: {a1.id}")

# 2. UNDER REVIEW — officer picked it up
a2 = make_app(jean, biz_reg, "under_review",
              "Rwanda Fresh Produce", "sole_proprietorship")
audit(a2, jean,    "application_created",   None,           "submitted",    {"service_code": "business-registration"})
audit(a2, officer, "status_transitioned",   "submitted",    "under_review", {"notes": "Documents look complete"})
notify(jean, "Application under review",
       f"Dear {jean.full_name}, your application is now being reviewed by our team.")
db.add(WorkflowTask(application=a2, assigned_officer_id=officer.id,
                    task_type="review", status="open"))

# 3. PAYMENT PENDING — completeness check passed
a3 = make_app(grace, biz_reg, "payment_pending",
              "Green Hills Construction", "partnership")
audit(a3, grace,   "application_created",   None,           "submitted",       {"service_code": "business-registration"})
audit(a3, officer, "status_transitioned",   "submitted",    "under_review",    {"notes": "Verified ID documents"})
audit(a3, officer, "status_transitioned",   "under_review", "payment_pending", {"notes": "Ready for payment"})
notify(grace, "Payment required",
       f"Dear {grace.full_name}, please pay the RWF 50,000 registration fee to continue.")

# 4. OFFICER REVIEW — payment confirmed, awaiting decision
a4 = make_app(patrick, biz_reg, "officer_review",
              "Muhanga Digital Services", "limited_company")
audit(a4, patrick, "application_created",  None,              "submitted",       {"service_code": "business-registration"})
audit(a4, officer, "status_transitioned",  "submitted",       "under_review",    {})
audit(a4, officer, "status_transitioned",  "under_review",    "payment_pending", {})
audit(a4, patrick, "payment_completed",    "payment_pending", "paid",
      {"provider": "mock", "reference": "MOCK-SEED4", "amount": "50000.00"})
audit(a4, officer, "status_transitioned",  "paid",            "officer_review",  {})
db.add(Payment(application_id=a4.id, provider="mock",
               provider_reference="MOCK-" + uuid.uuid4().hex[:12].upper(),
               amount=Decimal("50000.00"), currency="RWF", status="completed"))
notify(patrick, "Payment confirmed",
       f"Dear {patrick.full_name}, payment received. An officer will review your application.")
notify(patrick, "Under officer review",
       f"Dear {patrick.full_name}, your application is now under final officer review.")
db.add(WorkflowTask(application=a4, assigned_officer_id=officer.id,
                    task_type="review", status="open"))

# 5. APPROVED — everything passed
reg_num_5 = f"BR-{uuid.uuid4().hex[:8].upper()}"
a5 = make_app(diana, biz_reg, "approved",
              "Rubavu Innovation Hub", "limited_company",
              reg_number=reg_num_5)
audit(a5, diana,   "application_created",  None,              "submitted",       {})
audit(a5, officer, "status_transitioned",  "submitted",       "under_review",    {})
audit(a5, officer, "status_transitioned",  "under_review",    "payment_pending", {})
audit(a5, diana,   "payment_completed",    "payment_pending", "paid",
      {"provider": "mock", "reference": "MOCK-SEED5", "amount": "50000.00"})
audit(a5, officer, "status_transitioned",  "paid",            "officer_review",  {})
audit(a5, officer, "application_approved", "officer_review",  "approved",
      {"officer_id": str(officer.id)})
db.add(Payment(application_id=a5.id, provider="mock",
               provider_reference="MOCK-" + uuid.uuid4().hex[:12].upper(),
               amount=Decimal("50000.00"), currency="RWF", status="completed"))
notify(diana, "Application approved! 🎉",
       f"Dear {diana.full_name}, your business Rubavu Innovation Hub has been approved. "
       f"Registration number: {reg_num_5}")

# 6. COMPLETED — certificate issued
reg_num_6 = f"BR-{uuid.uuid4().hex[:8].upper()}"
a6 = make_app(alice, biz_reg, "completed",
              "Nyamirambo Textiles Co.", "partnership",
              reg_number=reg_num_6)
audit(a6, alice,   "application_created",  None,              "submitted",       {})
audit(a6, officer, "status_transitioned",  "submitted",       "under_review",    {})
audit(a6, officer, "status_transitioned",  "under_review",    "payment_pending", {})
audit(a6, alice,   "payment_completed",    "payment_pending", "paid",            {"provider": "mock"})
audit(a6, officer, "status_transitioned",  "paid",            "officer_review",  {})
audit(a6, officer, "application_approved", "officer_review",  "approved",        {})
audit(a6, officer, "status_transitioned",  "approved",        "completed",       {})
db.add(Payment(application_id=a6.id, provider="mock",
               provider_reference="MOCK-" + uuid.uuid4().hex[:12].upper(),
               amount=Decimal("50000.00"), currency="RWF", status="completed"))
notify(alice, "Certificate ready",
       f"Dear {alice.full_name}, your business certificate for Nyamirambo Textiles Co. "
       f"is ready for download. Registration: {reg_num_6}")

# 7. REJECTED
a7 = make_app(jean, biz_reg, "rejected",
              "Kigali Night Market", "sole_proprietorship",
              rejection_reason="ID document submitted is expired. Please renew and reapply.")
audit(a7, jean,   "application_created",  None,           "submitted",    {})
audit(a7, officer,"status_transitioned",  "submitted",    "under_review", {})
audit(a7, officer,"application_rejected", "under_review", "rejected",
      {"rejection_reason": "ID document submitted is expired. Please renew and reapply."})
notify(jean, "Application rejected",
       "Dear Jean Paul, unfortunately your application was rejected. "
       "Reason: ID document is expired. Please reapply with a valid ID.")

# 8. Demo citizen — one submitted for the demo account
a8 = make_app(demo_citizen, biz_reg, "submitted",
              "Demo Business Ltd", "limited_company")
audit(a8, demo_citizen, "application_created", None, "submitted",
      {"service_code": "business-registration"})
notify(demo_citizen, "Application received",
       "Dear Alice, your application for Demo Business Ltd has been received.")

db.commit()

print("DONE. Seeded:")
print(f"   {len(citizens)} citizen users")
print("   8 applications across all workflow states")
print("   Payments, audit logs, and notifications created")
print()
print("Demo login credentials:")
print("  citizen@bizreg.rw   / CitizenPass1234  (2 applications)")
print("  officer@bizreg.rw   / OfficerPass1234  (2 pending review tasks)")
print("  admin@bizreg.rw     / AdminPass12345   (full platform view)")

db.close()
