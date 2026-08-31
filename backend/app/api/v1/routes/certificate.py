"""Digital business-registration certificate generation (Day 6 / Day 12).

GET /applications/{id}/certificate

Only the owning citizen may download their certificate, and only when the
application is in 'approved' or 'completed' state.  The PDF is generated
on the fly with reportlab — no pre-rendered file is stored on disk.

Layout:
  - Government header bar (blue)
  - Republic of Rwanda seal text
  - Certificate title
  - Issued-to block (business name, type, owner, address)
  - Registration details (reg number, service, issue date)
  - Validity statement
  - Footer bar with application ID and platform name
"""

import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_role
from app.db.session import get_db
from app.models.application import Application
from app.models.user import User

router = APIRouter(prefix="/applications")

# ── Colours ──────────────────────────────────────────────────────────────────
BLUE_DARK  = colors.HexColor("#1e3a5f")   # header / footer background
BLUE_MID   = colors.HexColor("#2563eb")   # accent rule
GOLD       = colors.HexColor("#b8860b")   # seal accent
GREEN_DARK = colors.HexColor("#15803d")   # "APPROVED" stamp
SLATE      = colors.HexColor("#475569")   # body text
WHITE      = colors.white


def _build_certificate(app: Application, citizen: User) -> bytes:
    """Return raw PDF bytes for the given approved application."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Business Certificate – {app.registration_number}",
        author="BizReg — Republic of Rwanda",
    )

    styles = getSampleStyleSheet()
    W = A4[0] - 4 * cm  # usable width

    # ── Custom paragraph styles ───────────────────────────────────────────────
    def ps(name, **kw) -> ParagraphStyle:
        base = ParagraphStyle(name, parent=styles["Normal"], **kw)
        return base

    style_header_title = ps(
        "HeaderTitle",
        fontSize=11,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        alignment=1,
        leading=14,
    )
    style_seal = ps(
        "Seal",
        fontSize=9,
        textColor=WHITE,
        fontName="Helvetica-Oblique",
        alignment=1,
    )
    style_cert_title = ps(
        "CertTitle",
        fontSize=22,
        textColor=BLUE_DARK,
        fontName="Helvetica-Bold",
        alignment=1,
        spaceAfter=4,
    )
    style_cert_sub = ps(
        "CertSub",
        fontSize=11,
        textColor=SLATE,
        fontName="Helvetica-Oblique",
        alignment=1,
        spaceAfter=14,
    )
    style_body = ps(
        "Body",
        fontSize=10,
        textColor=SLATE,
        fontName="Helvetica",
        leading=16,
        alignment=1,
    )
    style_label = ps(
        "Label",
        fontSize=9,
        textColor=colors.HexColor("#94a3b8"),
        fontName="Helvetica",
    )
    style_value = ps(
        "Value",
        fontSize=11,
        textColor=BLUE_DARK,
        fontName="Helvetica-Bold",
        leading=14,
    )
    style_footer = ps(
        "Footer",
        fontSize=8,
        textColor=WHITE,
        fontName="Helvetica",
        alignment=1,
    )
    style_stamp = ps(
        "Stamp",
        fontSize=26,
        textColor=GREEN_DARK,
        fontName="Helvetica-Bold",
        alignment=1,
        borderColor=GREEN_DARK,
        borderWidth=2,
        borderPadding=6,
        borderRadius=4,
    )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def spacer(h_cm: float):
        return Spacer(1, h_cm * cm)

    def rule(color=BLUE_MID, thickness=1.5):
        return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6)

    form    = app.form_data or {}
    owner   = form.get("owner", {}) if isinstance(form.get("owner"), dict) else {}
    address = form.get("address", {}) if isinstance(form.get("address"), dict) else {}

    business_name = str(form.get("business_name", "—"))
    business_type = str(form.get("business_type", "—")).replace("_", " ").title()
    owner_name    = str(owner.get("full_name", "—"))
    owner_id      = str(owner.get("id_number", "—"))
    owner_phone   = str(owner.get("phone_number", "—"))
    addr_line     = str(address.get("line1", "—"))
    addr_city     = str(address.get("city", "—"))
    addr_district = str(address.get("district", "—"))
    addr_country  = str(address.get("country", "Rwanda"))
    reg_number    = str(app.registration_number or "—")
    issue_date    = datetime.now(timezone.utc).strftime("%d %B %Y")
    app_id_short  = str(app.id)[:8].upper()

    # ── Story ─────────────────────────────────────────────────────────────────
    story = []

    # --- Government header bar ------------------------------------------------
    header_data = [
        [Paragraph("REPUBLIC OF RWANDA", style_header_title)],
        [Paragraph("Ministry of Trade, Industry and Cooperatives", style_seal)],
        [Paragraph("Business Registration Authority", style_seal)],
    ]
    header_tbl = Table(header_data, colWidths=[W])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), BLUE_DARK),
        ("TOPPADDING",  (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(header_tbl)
    story.append(spacer(0.5))

    # --- Gold accent rule -----------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=3, color=GOLD, spaceAfter=16))

    # --- Certificate title ----------------------------------------------------
    story.append(Paragraph("CERTIFICATE OF BUSINESS REGISTRATION", style_cert_title))
    story.append(Paragraph("Issued under the laws of the Republic of Rwanda", style_cert_sub))
    story.append(rule())
    story.append(spacer(0.3))

    # --- Preamble paragraph ---------------------------------------------------
    preamble = (
        "This is to certify that the business described herein has been duly "
        "registered in accordance with the Business Registration Law of Rwanda "
        "and is authorised to conduct business within the territory of Rwanda."
    )
    story.append(Paragraph(preamble, style_body))
    story.append(spacer(0.5))

    # --- Business details table -----------------------------------------------
    def row(label: str, value: str):
        return [
            Paragraph(label.upper(), style_label),
            Paragraph(value, style_value),
        ]

    details = [
        row("Business Name",  business_name),
        row("Business Type",  business_type),
        row("Owner Name",     owner_name),
        row("Owner ID No.",   owner_id),
        row("Phone Number",   owner_phone),
        row("Business Address",
            f"{addr_line}, {addr_city}, {addr_district}, {addr_country}"),
    ]
    detail_tbl = Table(details, colWidths=[5 * cm, W - 5 * cm])
    detail_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1),
         [colors.HexColor("#f8fafc"), colors.HexColor("#f1f5f9")]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, -2),
         0.5, colors.HexColor("#e2e8f0")),
        ("BOX",           (0, 0), (-1, -1),
         1, colors.HexColor("#e2e8f0")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(detail_tbl)
    story.append(spacer(0.5))
    story.append(rule())
    story.append(spacer(0.3))

    # --- Registration details -------------------------------------------------
    reg_details = [
        row("Registration Number", reg_number),
        row("Service",             "Business Registration"),
        row("Date of Issue",       issue_date),
        row("Registered By",       "BizReg Digital Platform"),
        row("Certificate For",     citizen.full_name),
    ]
    reg_tbl = Table(reg_details, colWidths=[5 * cm, W - 5 * cm])
    reg_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#dcfce7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (-1, -2),
         0.5, colors.HexColor("#bbf7d0")),
        ("BOX",           (0, 0), (-1, -1),
         1, colors.HexColor("#86efac")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(reg_tbl)
    story.append(spacer(0.6))

    # --- APPROVED stamp -------------------------------------------------------
    story.append(Paragraph("✓  APPROVED  ✓", style_stamp))
    story.append(spacer(0.5))

    # --- Validity note --------------------------------------------------------
    story.append(rule(color=GOLD, thickness=1))
    validity = (
        "<i>This certificate is valid from the date of issue and remains in effect "
        "while the registered business complies with all applicable Rwandan laws and "
        "regulations. Any change in ownership, business name, or principal activity "
        "must be reported to the Business Registration Authority within 30 days.</i>"
    )
    story.append(Paragraph(
        validity,
        ps("Validity", fontSize=8, textColor=SLATE, fontName="Helvetica-Oblique",
           alignment=1, leading=12),
    ))
    story.append(spacer(0.6))

    # --- Footer bar -----------------------------------------------------------
    footer_data = [[
        Paragraph(
            f"Application ID: {app_id_short}  ·  "
            f"Verification: bizreg.gov.rw/verify/{reg_number}  ·  "
            f"BizReg Digital Platform  ·  {issue_date}",
            style_footer,
        )
    ]]
    footer_tbl = Table(footer_data, colWidths=[W])
    footer_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(footer_tbl)

    doc.build(story)
    return buf.getvalue()


# ── Route ─────────────────────────────────────────────────────────────────────

@router.get("/{application_id}/certificate")
def download_certificate(
    application_id: str,
    current_user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Stream a PDF business-registration certificate.

    Only the owning citizen may download their certificate.
    The application must be in 'approved' or 'completed' state.
    """
    application = db.scalar(
        select(Application)
        .options(
            joinedload(Application.service),
            joinedload(Application.citizen),
        )
        .where(
            Application.id == application_id,
            Application.citizen_id == current_user.id,
        )
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status_code not in ("approved", "completed"):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Certificate is only available for approved or completed applications. "
                f"Current status: '{application.status_code}'"
            ),
        )

    if not application.registration_number:
        raise HTTPException(
            status_code=422,
            detail="Registration number has not been assigned yet. Contact support.",
        )

    pdf_bytes = _build_certificate(application, current_user)

    safe_name = (
        application.form_data.get("business_name", "certificate")
        if isinstance(application.form_data, dict)
        else "certificate"
    )
    # Strip characters that are invalid in filenames
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in " _-").strip()
    safe_name = safe_name[:50] or "certificate"
    filename  = f"BizReg_Certificate_{safe_name}_{application.registration_number}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "no-store",
        },
    )
