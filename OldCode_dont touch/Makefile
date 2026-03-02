.PHONY: lint format test

lint:
	@echo "Running linter... (placeholder)"

format:
	@echo "Running formatter... (placeholder)"

test:
	@echo "Running tests... (placeholder)"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

demo-m0:
	docker compose up -d
	@echo "Waiting for API to be healthy..."
	@sleep 5
	curl -s http://localhost:8000/api/v1/health
	@echo ""
	@echo "Status check complete."
