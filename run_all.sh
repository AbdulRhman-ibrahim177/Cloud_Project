#!/bin/bash

echo "🚀 Starting Kafka cluster..."
cd kafka
docker-compose up -d
cd ..

echo "🔄 Waiting for Kafka to be ready..."
sleep 10

echo "📌 Creating Kafka topics..."
cd kafka
./create-topics.sh
cd ..

echo "🚀 Starting application services..."
docker-compose -f cloud-compose.yml up -d

echo "🔥 All services started successfully!"
echo "➡ API Gateway: http://localhost:8000"
echo "➡ TTS Service: http://localhost:8002"
echo "➡ STT Service: http://localhost:8003"
echo "➡ Prometheus: http://localhost:9090"
echo "➡ Grafana: http://localhost:3000"
