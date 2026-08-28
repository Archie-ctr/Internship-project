"""FastAPI application entry point.

The app factory-like composition is intentionally small at first. As phases add
middleware and routes, this file remains the readable map of API-wide behaviour.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Learning API for the BizReg digital business registration service.",
    debug=settings.debug,
)
# The frontend runs on a distinct localhost origin in development. This exact
# allow-list is safer than `*` and is sourced from the environment. Phase 9
# adds the remaining production security headers and rate limiting controls.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.backend_cors_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
