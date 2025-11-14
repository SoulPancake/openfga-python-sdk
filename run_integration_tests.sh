#!/bin/bash

set -e

echo "========================================="
echo "OpenFGA Python SDK Integration Tests"
echo "========================================="
echo ""

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

echo "Step 1: Starting OpenFGA server..."
docker compose -f docker-compose.integration-test.yml up -d

echo "Step 2: Waiting for server to be healthy..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose -f docker-compose.integration-test.yml ps | grep -q "healthy"; then
        echo "Server is healthy!"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo "Waiting... ($elapsed/$timeout seconds)"
done

if [ $elapsed -ge $timeout ]; then
    echo "Error: Server did not become healthy in time"
    docker compose -f docker-compose.integration-test.yml logs
    docker compose -f docker-compose.integration-test.yml down
    exit 1
fi

echo ""
echo "Step 3: Running integration tests..."
python -m pytest test/integration_error_handling_test.py -v -s || {
    echo ""
    echo "Tests failed. Cleaning up..."
    docker compose -f docker-compose.integration-test.yml down
    exit 1
}

echo ""
echo "Step 4: Cleaning up..."
docker compose -f docker-compose.integration-test.yml down

echo ""
echo "========================================="
echo "All integration tests passed!"
echo "========================================="
