FROM python:3.11-slim AS base

# Optional packaging — the v1 deploy story is a local binary, not Docker.
# This image exists for CI smoke tests and for buyers who explicitly want
# a containerized form factor. See docs/validation.md §4.

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build context is the monorepo root.
COPY packages/axon-core-py /kernel/axon-core-py
COPY packages/axon-historian /kernel/axon-historian
COPY apps/05-historian-bridge /app

RUN pip install /kernel/axon-core-py /kernel/axon-historian \
    && pip install /app[influx] \
    && pip install "fastapi>=0.115" "uvicorn[standard]>=0.30"

EXPOSE 8080
# Inside a container the only sensible bind is 0.0.0.0; the host should
# publish the port to a loopback or trusted interface only.
ENV HISTORIAN_BRIDGE_HOST=0.0.0.0 HISTORIAN_BRIDGE_PORT=8080
CMD ["historianbridge", "serve"]
