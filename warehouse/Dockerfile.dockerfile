# Warehouse Management System Dockerfile
# Supports OOP & VVRPO Course Project

FROM python:3.9-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL version="1.0"
LABEL description="Warehouse Management System - OOP & VVRPO Project"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Set work directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser $APP_HOME
USER appuser

# Create data directory
RUN mkdir -p $APP_HOME/data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('warehouse.db'); conn.close(); print('Database OK')" || exit 1

# Run the application
CMD ["python", "warehouse_final.py"]