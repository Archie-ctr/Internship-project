from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Check whether the API is running")
async def health_check() -> dict[str, str]:
    """A dependency-free probe suitable before database setup in Phase 2."""
    return {"status": "ok", "service": "bizreg-api"}
