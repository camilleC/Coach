VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
PDF_FILE = ./data/coaching.pdf

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make setup     - Create virtual environment and install dependencies"
	@echo "  make install   - Install/update dependencies only"
	@echo "  make ingest    - Ingest PDF into vector database"
	@echo "  make query Q='your question'  - Test a query"
	@echo "  make serve     - Launch the Gradio UI"
	@echo "  make clean     - Remove virtual environment and storage"
	@echo "  make reset-db  - Clear vector database only"

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
	PYTHONPATH=./src $(PYTHON) -m coach.ui.gradio_app --pdf $(PDF_FILE) --rebuild

# Test query (usage: make query Q="How do I set goals?")
.PHONY: query
query:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make query Q='your question here'"; \
		exit 1; \
	fi
	PYTHONPATH=./src $(PYTHON) -m coach.ui.gradio_app --query "$(Q)"

# Launch UI
.PHONY: serve
serve:
	PYTHONPATH=./src $(PYTHON) -m coach.ui.gradio_app --serve

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