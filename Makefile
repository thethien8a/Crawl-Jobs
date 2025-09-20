# CrawlJob Makefile - Automation Scripts
.PHONY: help setup dev up down clean test lint docs

# Default target
help:
	@echo "CrawlJob - Data Engineering Project"
	@echo ""
	@echo "Available commands:"
	@echo "  setup     - Initial project setup"
	@echo "  dev       - Start development environment"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  clean     - Clean up generated files"
	@echo "  test      - Run all tests"
	@echo "  lint      - Run code linting"
	@echo "  docs      - Generate documentation"
	@echo "  crawl     - Run job crawling"
	@echo "  sync      - Sync data to DuckDB"

# Setup project
setup:
	@echo "Setting up CrawlJob project..."
	python -m venv .venv
	.\.venv\Scripts\activate && pip install -r requirements.txt
	cp env.example .env
	@echo "Setup complete! Edit .env file with your credentials."

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d db
	sleep 5
	.\.venv\Scripts\activate && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d

# Stop services
down:
	@echo "Stopping services..."
	docker-compose down

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf .pytest_cache/
	rm -rf logs/*.log
	rm -rf outputs/*.json
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Run tests
test:
	@echo "Running tests..."
	.\.venv\Scripts\activate && python -m pytest test/ -v

# Code linting
lint:
	@echo "Running code linting..."
	.\.venv\Scripts\activate && flake8 CrawlJob/ api/ web/js/
	.\.venv\Scripts\activate && black --check CrawlJob/ api/

# Generate documentation
docs:
	@echo "Generating documentation..."
	.\.venv\Scripts\activate && pdoc --html --output-dir docs CrawlJob/
	@echo "Documentation generated in docs/ folder"

# Run job crawling
crawl:
	@echo "Starting job crawling..."
	.\.venv\Scripts\activate && python run_spider.py --spider all --keyword "Data Engineer"

# Sync data to DuckDB
sync:
	@echo "Syncing data to DuckDB..."
	.\.venv\Scripts\activate && python PyAirbyte/airbyte.py

# Data quality checks
quality:
	@echo "Running data quality checks..."
	.\.venv\Scripts\activate && soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check1.yml
	.\.venv\Scripts\activate && soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check2.yml
	.\.venv\Scripts\activate && soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check3.yml
