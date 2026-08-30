"""Document upload and download endpoints (Day 8).

Files are stored on the local filesystem under `settings.document_storage_path`.
The path hierarchy is `<root>/<application_id>/<uuid>_<original_filename>`.
A production deployment would swap the storage backend for S3 without changing
the route handler — that's the storage-abstraction pattern taught in Day 9.

Allowed types and size limits enforce the security requirements from Day 10:
  - Content-type checked server-side (browser MIME is untrusted)
  - Max file size: 10 MB
  - Allowed extensions: pdf, jpg, jpeg, png
"""

import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_role
from app.core.config import settings
from app.db.session import get_db
from app.models.application import Application
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/applications")

# ── Security constraints ─────────────────────────────────────────────────────
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    document_type: str
    original_filename: str
    content_type: str
    size_bytes: int


def _get_citizen_application(
    application_id: str, current_user: User, db: Session
) -> Application:
    """Load an application that belongs to the current citizen; raise 404 otherwise."""
    application = db.scalar(
        select(Application)
        .options(joinedload(Application.citizen))
        .where(Application.id == application_id, Application.citizen_id == current_user.id)
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post(
    "/{application_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    application_id: str,
    document_type: str,
    file: UploadFile,
    current_user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """Upload a supporting document for an application.

    Only the owning citizen may upload documents. The application must not be
    in a terminal state (approved, rejected, completed).
    """
    application = _get_citizen_application(application_id, current_user, db)

    terminal_states = {"approved", "rejected", "completed"}
    if application.status_code in terminal_states:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Documents cannot be added to an application in '{application.status_code}' state",
        )

    # Validate file extension against the allow-list (server-side check).
    original_filename = file.filename or "upload"
    suffix = Path(original_filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '{suffix}' is not allowed. Accepted types: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # Read the file bytes and check size before writing to disk.
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit",
        )
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty",
        )

    # Determine and validate MIME type from actual content (not browser header).
    guessed_type, _ = mimetypes.guess_type(original_filename)
    content_type = guessed_type or "application/octet-stream"
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"MIME type '{content_type}' is not allowed",
        )

    # Build a storage key that keeps files namespaced under their application.
    file_uuid = uuid.uuid4()
    storage_dir: Path = settings.document_storage_path / str(application_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_key = str(storage_dir / f"{file_uuid}{suffix}")

    with open(storage_key, "wb") as f:
        f.write(file_bytes)

    document = Document(
        application_id=application.id,
        document_type=document_type,
        original_filename=original_filename,
        storage_key=storage_key,
        content_type=content_type,
        size_bytes=len(file_bytes),
    )
    db.add(document)
    db.add(
        AuditLog(
            application=application,
            actor=current_user,
            action="document_uploaded",
            from_state=application.status_code,
            to_state=application.status_code,
            details={"document_type": document_type, "filename": original_filename},
        )
    )
    db.commit()
    db.refresh(document)
    return DocumentResponse(
        id=document.id,
        application_id=document.application_id,
        document_type=document.document_type,
        original_filename=document.original_filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
    )


@router.get("/{application_id}/documents", response_model=list[DocumentResponse])
def list_documents(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    """List documents for an application.

    Citizens see only their own application's documents.
    Officers and admins can list any application's documents.
    """
    if current_user.role.name == "citizen":
        application = _get_citizen_application(application_id, current_user, db)
    else:
        application = db.scalar(
            select(Application).where(Application.id == application_id)
        )
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")

    documents = db.scalars(
        select(Document).where(Document.application_id == application_id)
    ).all()
    return [
        DocumentResponse(
            id=doc.id,
            application_id=doc.application_id,
            document_type=doc.document_type,
            original_filename=doc.original_filename,
            content_type=doc.content_type,
            size_bytes=doc.size_bytes,
        )
        for doc in documents
    ]


@router.get("/{application_id}/documents/{document_id}/download")
def download_document(
    application_id: str,
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """Serve the actual file bytes after authorisation.

    Citizens may only download documents from their own applications.
    Officers and admins may download any document.
    """
    if current_user.role.name == "citizen":
        _get_citizen_application(application_id, current_user, db)

    document = db.scalar(
        select(Document).where(
            Document.id == document_id, Document.application_id == application_id
        )
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(document.storage_key)
    if not file_path.exists():
        raise HTTPException(status_code=410, detail="File no longer available in storage")

    return FileResponse(
        path=str(file_path),
        media_type=document.content_type,
        filename=document.original_filename,
    )
