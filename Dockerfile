# docker build -t travelmap:v1 .
# docker run -p 5001:5001 <image>
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifest + lockfile first for better layer caching.
# uv.lock* allows the build to succeed even before the lockfile is generated.
COPY pyproject.toml uv.lock* readme.MD ./

# Install runtime dependencies into /app/.venv (no project install since this is a flat-script app).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen --no-install-project

# Put the venv on PATH so `python3` resolves to the synced env
ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv"

# Copy application source
COPY . /app

# Will be mounted in for persistence as a PV
VOLUME /mnt
COPY *Tracker* /mnt

# Run as non-root
RUN useradd --create-home --shell /bin/sh worker && \
    chown -R worker:worker /app /mnt
USER worker

EXPOSE 5001

ENTRYPOINT ["python3"]
CMD ["runApp.py"]