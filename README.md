# RAG Tutor - AI-Powered Document Q&A System

A comprehensive Retrieval-Augmented Generation (RAG) system with FastAPI backend, Gradio UI, and full observability via Prometheus and Grafana.

## Features

- **FastAPI Backend**: RESTful API with automatic retry logic and comprehensive error handling
- **Gradio UI**: User-friendly web interface for document Q&A
- **Full Observability**: Prometheus metrics and Grafana dashboards
- **Docker Support**: Complete containerization with docker-compose
- **Production Ready**: Proper logging, monitoring, and error handling
- **Local LLM Support**: Works with Ollama and other OpenAI-compatible endpoints

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Navigate to the ragtutor directory
cd ragtutor

# Build and run all services
docker compose up --build
```

Access the services:
- **API Documentation**: http://localhost:8000/docs
- **Gradio UI**: http://localhost:7860
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Option 2: Local Development
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Start API server
uvicorn ragtutor.api.main:app --host 0.0.0.0 --port 8000

# In another terminal, start Gradio UI
python -m ragtutor.ui.gradio_app
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
    "content": "<base64-encoded-pdf>",
    "collection_name": "documents"
  }'
```

## Configuration

Copy `.env.example` to `.env` and adjust settings:

```bash
# API Configuration
LOG_LEVEL=INFO
API_PORT=8000

# RAG Configuration
MODEL_NAME=llama3.2
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama

# Monitoring
PROMETHEUS_SCRAPE_INTERVAL=5s
GRAFANA_HOST_PORT=3000
PROMETHEUS_HOST_PORT=9090
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ragtutor

# Run specific test file
pytest ragtutor/tests/test_api.py
```

## Development

### Adding New Features
1. Add business logic in `ragtutor/core/`
2. Add API endpoints in `ragtutor/api/routes.py`
3. Add UI components in `ragtutor/ui/`
4. Add tests in `ragtutor/tests/`

### Monitoring
- **Prometheus**: Collects metrics from the FastAPI app
- **Grafana**: Visualizes RAG usage, query performance, and error rates
- **Custom Metrics**: Track query duration, error types, and vector operations

## Troubleshooting

### Common Issues
1. **LLM Connection**: Ensure Ollama is running at `LLM_BASE_URL`
2. **Port Conflicts**: Check if ports 8000, 7860, 9090, 3000 are available
3. **Memory Issues**: Reduce `chunk_size` in settings for large documents

### Logs
```bash
# View API logs
docker compose logs rag-api

# View UI logs  
docker compose logs rag-ui
```

## License

This project is open source and available under the MIT License.
