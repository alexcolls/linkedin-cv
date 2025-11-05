# LinkedIn CV Generator Dockerfile
# Optimized multi-stage build for production

# Build stage
FROM python:3.9-slim as builder

ARG PYTHON_VERSION=3.9

# Set working directory
WORKDIR /app

# Install system dependencies for building and WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without dev dependencies)
RUN poetry install --only main --no-interaction --no-ansi --no-root \
    && pip cache purge

# Install Playwright browsers with minimal deps
RUN poetry run playwright install chromium --with-deps \
    && rm -rf /root/.cache/ms-playwright/chromium-*/locales \
    && rm -rf /root/.cache/ms-playwright/chromium-*/chrome_crashpad_handler

# Runtime stage
FROM python:3.9-slim

# Labels for metadata
LABEL maintainer="LinkedIn CV Generator" \
      version="0.6.0" \
      description="Production-ready LinkedIn CV generator with beautiful templates"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright \
    PATH="/app:$PATH"

# Install runtime dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint dependencies
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi7 \
    shared-mime-info \
    # Playwright/Chromium dependencies
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /tmp/* /var/tmp/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash linkedin && \
    mkdir -p /app /data && \
    chown -R linkedin:linkedin /app /data

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application code
COPY --chown=linkedin:linkedin . .

# Switch to non-root user
USER linkedin

# Create output directory
RUN mkdir -p /data/output

# Expose volume mount points
VOLUME ["/data/output", "/app/sessions"]

# Health check (validate imports and dependencies)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "from src.config import Config; from src.pdf.generator import PDFGenerator; import sys; sys.exit(0)" || exit 1

# Entry point
ENTRYPOINT ["python3", "-m", "src.cli"]

# Default command (show help)
CMD ["--help"]
