FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install Python deps first (to leverage Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy source code
COPY src/ src/

# Set Python path so it can find the coach package
ENV PYTHONPATH=/app/src

# Create data directories (they can be mounted as volumes)
RUN mkdir -p /app/data /app/uploads

EXPOSE 8000 7860

# Default command
CMD ["uvicorn", "coach.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
