# VISIONZ Backend - Hugging Face Spaces Dockerfile

FROM python:3.10.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port for Hugging Face
EXPOSE 7860

# Run application on port 7860 (Hugging Face standard)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
