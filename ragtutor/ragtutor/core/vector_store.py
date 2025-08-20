from typing import Dict, List, Optional

import chromadb
from chromadb import PersistentClient

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGVectorStoreError
from ..utils.metrics import document_chunks_total


class VectorStore:
    def __init__(self, persist_directory: Optional[str] = None):
        try:
            self.client: PersistentClient = chromadb.PersistentClient(
                path=persist_directory or settings.vector_db_persist_dir
            )
        except Exception as exc:
            raise RAGVectorStoreError("Failed to initialize vector store") from exc

    def get_or_create_collection(self, name: str):
        try:
            return self.client.get_or_create_collection(name)
        except Exception as exc:
            raise RAGVectorStoreError("Failed to get or create collection", {"name": name}) from exc

    def add_chunks(self, collection_name: str, chunks: List[Dict[str, object]], embeddings: List[List[float]]):
        try:
            collection = self.get_or_create_collection(collection_name)
            ids = [chunk["id"] for chunk in chunks]
            texts = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
            document_chunks_total.labels(collection=collection_name).set(collection.count())
        except Exception as exc:
            raise RAGVectorStoreError("Failed to add chunks to vector store", {"collection": collection_name}) from exc

    def query(self, collection_name: str, query_embedding: List[float], top_k: int) -> Dict[str, List]:
        try:
            collection = self.get_or_create_collection(collection_name)
            results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
            return results
        except Exception as exc:
            raise RAGVectorStoreError("Failed to query vector store", {"collection": collection_name}) from exc

    def list_collections(self) -> List[str]:
        try:
            return [c.name for c in self.client.list_collections()]
        except Exception as exc:
            raise RAGVectorStoreError("Failed to list collections") from exc

