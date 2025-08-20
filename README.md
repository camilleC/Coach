README.md
# Local RAG with PDF

A Retrieval-Augmented Generation (RAG) system that works entirely locally using Chroma vector database and Ollama.

## Quick Start

### Option 1: Using Make (recommended)
```bash
# First time setup
make setup

# Ingest your PDF
make ingest

# Test a query
make query Q="How do I set goals with a client?"

# Launch UI
make serve
Option 2: Using setup script
# Make script executable (first time only)
chmod +x setup.sh

# First time setup
./setup.sh setup

# Ingest your PDF
./setup.sh ingest

# Test a query
./setup.sh query "How do I set goals with a client?"

# Launch UI
./setup.sh serve
Option 3: Manual setup
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Follow the original workflow...
Project Structure
.
├── rag_local_pdf.py      # Main application
├── requirements.txt      # Python dependencies
├── Makefile             # Automation commands
├── setup.sh             # Alternative setup script
├── data/                # Your PDF files
│   └── coaching.pdf
├── storage/             # Vector database (auto-created)
├── .venv/               # Virtual environment
└── README.md
Commands Reference
* make help - Show all available commands
* make setup - One-time project setup
* make ingest - Process PDF into vector database
* make serve - Launch web interface
* make clean - Reset entire project
	•	make reset-db - Clear database only
## 5. .gitignore
Virtual environment
.venv/ venv/
Vector database storage
storage/
Python cache
pycache/ *.pyc *.pyo
Environment variables
.env
OS files
.DS_Store Thumbs.db
IDE files
.vscode/ .idea/ *.swp *.swo
