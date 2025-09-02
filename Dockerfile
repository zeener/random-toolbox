# Random Toolbox Microservice - Production Ready Container
FROM python:3.12-slim

# Set metadata
LABEL maintainer="István Sári <isari@example.com>"
LABEL description="Random Toolbox - Microservice for generating random text, passwords, and API keys"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    FLASK_APP=src.api.app \
    FLASK_ENV=production \
    PORT=8002

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY README.md LICENSE ./

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp

# Set proper permissions
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run the application
CMD ["sh", "-c", "python -m flask run --host=0.0.0.0 --port=${PORT}"]