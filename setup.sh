#!/bin/bash
set -e

echo "🚀 Starting Project Initialization (Dockerized)..."

# 1. Build and Start Containers
echo "🐳 Building Docker images..."
sudo docker compose up -d --build

# 2. Initialize Database (Run inside container)
echo "🗄️ Initializing Database Connection & Schema..."
# Wait for DB to be ready might be needed, but let's try running init script
sleep 5 # Grace period
sudo docker compose exec -T etl python src/db/connection.py

# 3. Verify
echo "🧪 Running Verification Tests..."
sudo docker compose exec -T etl python tests/verify_setup.py

echo "✅ Initialization Complete!"
echo "To run extraction: sudo docker compose exec etl python src/etl/extract_bolsa_familia.py"
