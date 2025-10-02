# Multi-stage build for optimization
FROM python:3.11-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash polyglotai44

# Set working directory and create necessary directories as root
WORKDIR /home/polyglotai44/app
RUN mkdir -p data logs exports && chown -R polyglotai44:polyglotai44 /home/polyglotai44/app

# Copy application code
COPY --chown=polyglotai44:polyglotai44 . .

# Switch to non-root user
USER polyglotai44

# Set environment variables
ENV PYTHONPATH=/home/polyglotai44/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import asyncio; import asyncpg; import os; asyncio.run(asyncpg.connect(os.getenv('DATABASE_URL')).close())" || exit 1

# Expose port (if using webhooks)
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]