FROM python:3.11-slim

WORKDIR /app

COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables for Kafka connection
ENV KAFKA_BROKERS="localhost:39092,localhost:39093,localhost:39094"
ENV AWS_REGION="us-east-1"

# Expose port
EXPOSE 8003

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
