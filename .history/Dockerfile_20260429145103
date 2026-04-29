FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy kernel packages and the app — assumes monorepo build context.
COPY packages/axon-core-py /kernel/axon-core-py
COPY packages/axon-historian /kernel/axon-historian
COPY apps/05-historian-bridge /app

RUN pip install /kernel/axon-core-py /kernel/axon-historian \
    && pip install /app[influx] \
    && pip install "fastapi>=0.115" "uvicorn[standard]>=0.30"

EXPOSE 8080
ENV HISTORIAN_BRIDGE_HOST=0.0.0.0 HISTORIAN_BRIDGE_PORT=8080
CMD ["python", "-m", "historian_bridge"]
