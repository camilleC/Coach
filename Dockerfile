FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/src/

# Set Python path so it can find the coach package
ENV PYTHONPATH=/app/src

# Create necessary directories (data will be mounted as volume)
RUN mkdir -p /app/data /app/uploads

EXPOSE 8000 7860

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "coach.api.main:app", "--host", "0.0.0.0", "--port", "8000"]