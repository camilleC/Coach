VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
PYTHONPATH_PREFIX = PYTHONPATH=./src
PDF_FILE = ./data/coaching.pdf
QDRANT_URL = http://localhost:6333

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make setup     - Create virtual environment and install dependencies"
	@echo "  make install   - Install/update dependencies only"
	@echo "  make ingest    - Ingest PDF into vector database"
	@echo "  make query Q='your question'  - Test a query"
	@echo "  make serve        - Launch the Gradio UI"
	@echo "  make rag_tests    - Run RAG tests (tests/ directory)"
	@echo "  make tests        - Run all tests locally"
	@echo "  make docker-tests - Run tests inside Docker"
	@echo "  make up           - Run the project with docker-compose"
	@echo "  make down         - Stop docker-compose services"
	@echo "  make clean        - Remove virtual environment and storage"
	@echo "  make reset-db     - Clear vector database only"

# Setup virtual environment and install dependencies
.PHONY: setup
setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Setup complete! Virtual environment created and dependencies installed."

# Install/update dependencies only
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Ingest PDF
.PHONY: ingest
ingest:
	PDF=$(PDF_FILE) QDRANT_URL=$(QDRANT_URL) $(PYTHONPATH_PREFIX) $(PYTHON) -m coach.ui.gradio_app --pdf $(PDF_FILE) --rebuild

# Test query (usage: make query Q="How do I set goals?")
.PHONY: query
query:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make query Q='your question here'"; \
		exit 1; \
	fi
	PDF=$(PDF_FILE) QDRANT_URL=$(QDRANT_URL) $(PYTHONPATH_PREFIX) $(PYTHON) -m coach.ui.gradio_app --query "$(Q)"

# Run Rag related tests (locally)
.PHONY: rag_tests
rag_tests:
	PDF=$(PDF_FILE) QDRANT_URL=$(QDRANT_URL) $(PYTHONPATH_PREFIX) $(PYTHON) -m pytest tests -v

# Run application tests (locally)
.PHONY: tests
tests:
	PDF=$(PDF_FILE) QDRANT_URL=$(QDRANT_URL) $(PYTHONPATH_PREFIX) $(PYTHON) -m pytest tests src/coach/tests

# Run tests inside Docker
.PHONY: docker-tests
docker-tests:
	docker-compose exec rag-api pytest -v

# Launch UI
.PHONY: serve
serve:
	@lsof -ti:7860 | xargs kill -9 2>/dev/null || true
	PDF=$(PDF_FILE) QDRANT_URL=$(QDRANT_URL) $(PYTHONPATH_PREFIX) $(PYTHON) -m coach.ui.gradio_app --serve

# Run with docker-compose
.PHONY: up
up:
	docker-compose up

# Stop docker-compose services
.PHONY: down
down:
	docker-compose down

# Clean up
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -rf ./data/chroma ./data/vector_store

# Clear vector database only
.PHONY: reset-db
reset-db:
	rm -rf ./data/chroma ./data/vector_store
	@echo "Vector database cleared. Run 'make ingest' to rebuild."