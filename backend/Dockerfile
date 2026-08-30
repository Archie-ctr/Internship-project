# ── Stage 1: dependency installation ────────────────────────────────────────
FROM python:3.13-slim AS deps

WORKDIR /app

# System libraries needed to compile psycopg (libpq) and bcrypt.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: production image ────────────────────────────────────────────────
FROM python:3.13-slim AS production

WORKDIR /app

# Only the shared C libraries; no compiler toolchain in the final image.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from the deps stage (keeps the image smaller).
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source.
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/

# Non-root user for security — running as root inside a container is a
# common Docker hardening failure that the Day-10 security module covers.
RUN addgroup --system bizreg && adduser --system --ingroup bizreg bizreg
USER bizreg

# Document upload storage directory (local dev path from Settings).
RUN mkdir -p /app/storage/documents

EXPOSE 8000

# uvicorn[standard] is already in requirements.txt via the base install.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
