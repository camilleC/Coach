from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
import os

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGVectorStoreError
from ..utils.metrics import document_chunks_total


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None):
        try:
            # Use QdrantClient for a local instance with on-disk persistence
            path = persist_directory or settings.vector_db_persist_dir
            # Ensure the directory exists
            os.makedirs(path, exist_ok=True)
            self.client: QdrantClient = QdrantClient(path=path)
        except Exception as exc:
            raise RAGVectorStoreError("Failed to initialize vector store") from exc

    def get_or_create_collection(self, name: str):
        try:
            # Check if the collection exists
            collections = self.client.get_collections().collections
            if name not in [c.name for c in collections]:
                # If not, create it
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
                )
            return self.client.get_collection(collection_name=name)
        except Exception as exc:
            raise RAGVectorStoreError("Failed to get or create collection", {"name": name}) from exc

    def add_chunks(self, collection_name: str, chunks: List[Dict[str, object]], embeddings: List[List[float]]):
        try:
            # Ensure the collection exists before adding points
            self.get_or_create_collection(collection_name)

            points = [
                PointStruct(
                    id=chunk["id"],
                    vector=embeddings[i],
                    payload={"text": chunk["text"], **chunk["metadata"]},
                )
                for i, chunk in enumerate(chunks)
            ]
            self.client.upsert(
                collection_name=collection_name,
                wait=True,
                points=points,
            )
            # Retrieve the count and update the metric
            collection_info = self.client.count(collection_name=collection_name, exact=True)
            document_chunks_total.labels(collection=collection_name).set(collection_info.count)

        except Exception as exc:
            raise RAGVectorStoreError("Failed to add chunks to vector store", {"collection": collection_name}) from exc

    def query(self, collection_name: str, query_embedding: List[float], top_k: int) -> List[Dict[str, object]]:
        try:
            self.get_or_create_collection(collection_name)
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
            )
            
            # The return format is a list of ScoredPoint objects, so we need to
            # convert it to the format your RAGService expects.
            formatted_results = []
            for point in results:
                formatted_results.append({
                    "documents": point.payload.get("text"),
                    "metadatas": {k: v for k, v in point.payload.items() if k != "text"},
                    "distances": 1 - point.score, # Convert similarity score to distance
                })
            
            return formatted_results
        except Exception as exc:
            raise RAGVectorStoreError("Failed to query vector store", {"collection": collection_name}) from exc

    def list_collections(self) -> List[str]:
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as exc:
            raise RAGVectorStoreError("Failed to list collections") from exc