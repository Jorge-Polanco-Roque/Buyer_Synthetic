# Multi-stage build for Buyer Synthetic™
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.4

# Set work directory
WORKDIR /app

# Copy poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure poetry: disable virtual env creation as we'll use the container as env
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8505 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r buyer && useradd -r -g buyer buyer

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create app directory
WORKDIR /app

# Copy application code
COPY src/ /app/src/
COPY agentes/ /app/agentes/
COPY funciones/ /app/funciones/
COPY contexto/ /app/contexto/
COPY prompts/ /app/prompts/
COPY run.py /app/
COPY test_*.py /app/
COPY *.md /app/

# Create data directories
RUN mkdir -p /app/data/{input,output,temp} /app/logs && \
    chown -R buyer:buyer /app

# Switch to non-root user
USER buyer

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8505/_stcore/health || exit 1

# Expose port
EXPOSE 8505

# Default command - run dashboard
CMD ["python", "-m", "streamlit", "run", "src/ui/dashboard.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8505"]