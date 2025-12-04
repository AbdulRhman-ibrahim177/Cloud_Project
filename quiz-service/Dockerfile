FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Resource requirements: 2 CPU, 4GB RAM
# Set in docker-compose or k8s

# Default command - run API server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
