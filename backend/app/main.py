"""FastAPI application entry point.

The app factory-like composition is intentionally small. As phases add
middleware and routes, this file remains the readable map of API-wide behaviour.

Security controls applied here (Day 10):
  - CORS with explicit origin, method, and header allow-lists
  - Rate limiting via slowapi (Redis-backed in production, in-memory for tests)
  - Trusted host checking can be added via TrustedHostMiddleware in production
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings

# ── Rate limiter ─────────────────────────────────────────────────────────────
# The key function uses the client IP; behind a reverse proxy, set
# FORWARDED_ALLOW_IPS and use X-Forwarded-For instead.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "BizReg — Digital public-service platform API. "
        "Built following the SecureAI Labs 14-Day curriculum."
    ),
    debug=settings.debug,
)

# Attach the limiter so route decorators (@limiter.limit) work and the
# 429 handler returns a consistent JSON body.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ─────────────────────────────────────────────────────────────────────
# PUT and PATCH are required by future update endpoints (officer workflow,
# profile management). DELETE is required for document removal.
# allow_credentials is True so cookie-based auth can be layered on later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.backend_cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirect bare root to the interactive API docs."""
    return RedirectResponse(url="/docs")
