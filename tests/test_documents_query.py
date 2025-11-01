# test_documents_query.py
# test_documents_query_fixed.py
from qdrant_client import QdrantClient
import os

host = os.getenv("VECTOR_DB_HOST", "localhost")
port = int(os.getenv("VECTOR_DB_PORT", "6333"))

client = QdrantClient(host=host, port=port)

collection = "documents"

# Scroll to get first 3 points
result, _scroll_id = client.scroll(collection_name=collection, limit=3)

print(f"First 3 points in '{collection}':")
for p in result:
    print(f"ID: {p.id}, Payload: {p.payload}, Vector length: {len(p.vector) if p.vector else 'None'}")

