# Coach - AI-Powered Document Q&A System

Retrieval-Augmented Generation (RAG) system with FastAPI backend, Gradio UI, Qdrant vector database, and full observability via Prometheus and Grafana.


## NOTES
- This is a work in progress. The next task is cleaning up the makefile. 
- My solution contains a A pdf with information on coaching but it is not checked into git.

## Features

- **FastAPI Backend**: RESTful API with automatic retry logic and comprehensive error handling
- **Gradio UI**: User-friendly "Personal Coach" web interface for document Q&A
- **Qdrant Vector Database**: Efficient vector storage and similarity search
- **Full Observability**: Prometheus metrics and Grafana dashboards
- **Docker Support**: Complete containerization with docker-compose
- **Production Ready**: Proper logging, monitoring, and error handling
- **Local LLM Support**: Works with Ollama and other OpenAI-compatible endpoints

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Build and run all services
docker-compose up --build
```

Access the services:
- **API Documentation**: http://localhost:8000/docs
- **Gradio UI**: http://localhost:7860
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Qdrant**: http://localhost:6333

### Option 2: Local Development with Makefile
```bash
# Setup virtual environment and install dependencies
make setup

# Ingest PDF into vector database
make ingest

# Launch the Gradio UI
make serve

# Test a query
make query Q="How do I set goals?"
```

### Option 3: Manual Local Development
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start API server (requires Qdrant running)
PYTHONPATH=./src uvicorn coach.api.main:app --host 0.0.0.0 --port 8000

# In another terminal, start Gradio UI
PYTHONPATH=./src python -m coach.ui.gradio_app
```

## API Usage

### Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key coaching principles?",
    "top_k": 5,
    "collection_name": "documents"
  }'
```

### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "coaching.pdf",
    "content": "<pdf-bytes>",
    "collection_name": "documents"
  }'
```

### List Collections
```bash
curl -X GET "http://localhost:8000/collections"
```

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

## Configuration

Environment variables (set in `.env` or via environment):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Vector Database (Qdrant)
VECTOR_DB_HOST=qdrant
VECTOR_DB_PORT=6333
COLLECTION_NAME=documents
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM=384

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K=5
PDF=/app/data/coaching.pdf

# LLM Configuration
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_TIMEOUT=30
MAX_TOKENS=512

# Monitoring
PROMETHEUS_HOST_PORT=9090
GRAFANA_HOST_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

## Testing

```bash
# Run RAG tests
make rag_tests

# Run all tests (RAG + application tests)
make tests

# Run tests inside Docker
make docker-tests

# Or use pytest directly
PYTHONPATH=./src pytest tests
PYTHONPATH=./src pytest src/coach/tests
```
### Monitoring
- **Prometheus**: Collects metrics from the FastAPI app
- **Grafana**: Visualizes RAG usage, query performance, and error rates
- **Custom Metrics**: Track query duration, error types, and vector operations

## Troubleshooting

### Common Issues
1. **LLM Connection**: Ensure Ollama is running at `LLM_BASE_URL`
2. **Qdrant Connection**: Ensure Qdrant is running at port 6333
3. **Port Conflicts**: Check if ports 8000, 7860, 9090, 3000, 6333 are available
4. **Memory Issues**: Reduce `CHUNK_SIZE` for large documents

### Logs
```bash
# View API logs
docker-compose logs rag-api

# View UI logs  
docker-compose logs rag-ui

# View Qdrant logs
docker-compose logs qdrant
```
