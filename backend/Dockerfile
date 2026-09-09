# BEM 100 v2.0 - Free-Tier Container Dockerfile (< 512MB RAM guardrail)
FROM python:3.11-slim

WORKDIR /app

# Prevent python from buffering stdout/stderr and writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application source
COPY bem_engine /app/bem_engine
COPY data_provider /app/data_provider
COPY database /app/database
COPY backend /app/backend
COPY scripts /app/scripts

EXPOSE 8000

# Run uvicorn with 1 worker to strictly respect free tier < 512MB memory
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
