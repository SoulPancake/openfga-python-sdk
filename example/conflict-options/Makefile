.PHONY: help start stop status run clean logs

# Default target
help:
	@echo "OpenFGA Conflict Options Example"
	@echo "================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make start   - Start OpenFGA server and database"
	@echo "  make stop    - Stop OpenFGA server and database"
	@echo "  make status  - Check status of services"
	@echo "  make run     - Run the conflict options demo"
	@echo "  make logs    - Show logs from OpenFGA server"
	@echo "  make clean   - Stop services and remove volumes"
	@echo ""

# Start the OpenFGA server and database
start:
	@echo "Starting OpenFGA services..."
	docker compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services started. OpenFGA is available at:"
	@echo "  - API:        http://localhost:8080"
	@echo "  - Playground: http://localhost:3000"

# Stop the services
stop:
	@echo "Stopping OpenFGA services..."
	docker compose down

# Check service status
status:
	@echo "Checking service status..."
	@docker compose ps

# Run the conflict options demo
run:
	@echo "Running conflict options demo..."
	@echo ""
	python3 conflict_options_example.py

# Show logs from OpenFGA
logs:
	@echo "Showing OpenFGA logs (Ctrl+C to exit)..."
	docker compose logs -f openfga

# Clean up everything including volumes
clean:
	@echo "Cleaning up all services and volumes..."
	docker compose down -v
	@echo "Cleanup complete"

# Run everything: start services, wait, run demo, stop
demo: start
	@echo "Waiting for OpenFGA to be fully ready..."
	@sleep 10
	@make run
	@echo ""
	@echo "Demo complete! Services are still running."
	@echo "Run 'make stop' to stop the services."
