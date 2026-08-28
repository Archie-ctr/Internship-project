from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.service import Service
from app.schemas.service import ServiceResponse

router = APIRouter(prefix="/services")


@router.get("", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)) -> list[Service]:
    """Return active catalogue services, ready to expand beyond registration."""
    return list(db.scalars(select(Service).where(Service.is_active.is_(True)).order_by(Service.name)))
