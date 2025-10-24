FROM python:3.11-slim

# Install system dependencies for gpiozero and pigpio
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    pigpio \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables for uv
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Copy dependency files for better caching
COPY pyproject.toml uv.lock ./

# Sync dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI app with uvicorn using uv run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

