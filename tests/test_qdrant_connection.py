from qdrant_client import QdrantClient
import os

host = os.getenv("VECTOR_DB_HOST", "localhost")
port = int(os.getenv("VECTOR_DB_PORT", "6333"))

print(f"Trying to connect to Qdrant at {host}:{port}")

try:
    client = QdrantClient(host=host, port=port)
    # List collections to verify connection
    collections = client.get_collections()
    print("Collections:", [c.name for c in collections.collections])
except Exception as e:
    print(f"Qdrant connection failed: {e}")
