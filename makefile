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
	$(PIP) install -r ragtutor/requirements.txt
	@echo "Setup complete! Virtual environment created and dependencies installed."

# Install/update dependencies only
.PHONY: install
install:
	$(PIP) install -r ragtutor/requirements.txt

# Ingest PDF
.PHONY: ingest
ingest:
	$(PYTHON) ragtutor/ui/gradio_app.py --pdf $(PDF_FILE) --rebuild

# Test query (usage: make query Q="How do I set goals?")
.PHONY: query
query:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make query Q='your question here'"; \
		exit 1; \
	fi
	$(PYTHON) ragtutor/ui/gradio_app.py --query "$(Q)"

# Launch UI
.PHONY: serve
serve:
	$(PYTHON) ragtutor/ui/gradio_app.py --serve

# Clean up
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -rf ./storage

# Clear vector database only
.PHONY: reset-db
reset-db:
	rm -rf ./storage
	@echo "Vector database cleared. Run 'make ingest' to rebuild."