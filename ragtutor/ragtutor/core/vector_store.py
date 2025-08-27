# ragtutor/core/vector_store.py

from __future__ import annotations

from typing import Dict, List, Optional, Any
import os
import logging

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGVectorStoreError
from ..utils.metrics import document_chunks_total

logger = logging.getLogger(__name__)


def _infer_dim_from_model(model_name: Optional[str]) -> int:
    """
    Fallback when settings.embedding_dim isn't present.
    Covers a few common embedders; defaults to 384.
    """
    if not model_name:
        return 384
    name = model_name.lower()
    if "all-minilm-l6-v2" in name:
        return 384
    if "e5-small" in name:
        return 384
    if "e5-base" in name:
        return 768
    if "e5-large" in name:
        return 1024
    if "text-embedding-3-small" in name:
        return 1536
    if "text-embedding-3-large" in name:
        return 3072
    return 384


class VectorStore:
    """
    Qdrant-backed vector store.

    Connection strategy (in order):
      1) QDRANT_URL (e.g. http://qdrant:6333) [+ optional QDRANT_API_KEY]
      2) Embedded mode if QDRANT_EMBEDDED=1 (or truthy): QDRANT_PATH or settings.vector_db_persist_dir
      3) Fallback URL http://localhost:6333

    Collection vector size is taken from:
      settings.embedding_dim (if present)
      else inferred from settings.embedding_model
      else default 384
    """

    def __init__(self, client: Optional[QdrantClient] = None) -> None:
        try:
            if client:
                self.client = client
                logger.info("Using injected QdrantClient.")
                return

            url = os.getenv("QDRANT_URL", "").strip()
            api_key = os.getenv("QDRANT_API_KEY", "").strip()
            embedded_flag = os.getenv("QDRANT_EMBEDDED", "").strip()

            if url:
                kwargs: Dict[str, Any] = {"url": url}
                if api_key:
                    kwargs["api_key"] = api_key
                self.client = QdrantClient(**kwargs)
                logger.info(f"Connecting to Qdrant at {url}")
            elif embedded_flag and embedded_flag.lower() not in ("0", "false", "no"):
                path = os.getenv("QDRANT_PATH", "./data/qdrant")
                os.makedirs(path, exist_ok=True)
                self.client = QdrantClient(path=path)
                logger.info(f"Starting embedded Qdrant at {path}")
            else:
                self.client = QdrantClient(url="http://localhost:6333")
                logger.info("Connecting to Qdrant at http://localhost:6333")
        except Exception as exc:
            raise RAGVectorStoreError("Failed to initialize vector store") from exc

        # Determine embedding dimension
        self._dim = getattr(settings, "embedding_dim", None)
        if not isinstance(self._dim, int):
            self._dim = _infer_dim_from_model(getattr(settings, "embedding_model", None))
            logger.warning(f"settings.embedding_dim not found; inferring dimension {self._dim}.")

    # -------------------------
    # Collections
    # -------------------------
    def get_or_create_collection(self, name: str):
        try:
            existing = [c.name for c in self.client.get_collections().collections]
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=self._dim, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection '{name}' (dim={self._dim}, distance=COSINE)")
            return self.client.get_collection(collection_name=name)
        except Exception as exc:
            raise RAGVectorStoreError("Failed to get or create collection", {"name": name}) from exc

    def list_collections(self) -> List[str]:
        try:
            return [c.name for c in self.client.get_collections().collections]
        except Exception as exc:
            raise RAGVectorStoreError("Failed to list collections") from exc

    # -------------------------
    # Ingestion
    # -------------------------
    def add_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, object]],
        embeddings: List[List[float]],
    ) -> None:
        try:
            if len(chunks) != len(embeddings):
                raise ValueError(
                    f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch"
                )
            self.get_or_create_collection(collection_name)

            points: List[PointStruct] = []
            for i, chunk in enumerate(chunks):
                cid = chunk.get("id")
                pid = cid if isinstance(cid, (int, str)) else str(cid) if cid is not None else None

                payload = {"text": chunk.get("text", "")}
                md = chunk.get("metadata") or {}
                if isinstance(md, dict):
                    payload.update(md)

                points.append(PointStruct(id=pid, vector=embeddings[i], payload=payload))

            self.client.upsert(collection_name=collection_name, points=points, wait=True)
            count = self.client.count(collection_name=collection_name, exact=True).count
            document_chunks_total.labels(collection=collection_name).set(count)
            logger.info(f"Upserted {len(points)} points into '{collection_name}'. Total={count}")
        except Exception as exc:
            logger.error(f"Detailed error while adding chunks to vector store '{collection_name}': {exc}", exc_info=True)
            logger.error(f"Chunks: {chunks[:2]} (showing up to 2), Embeddings shape: {len(embeddings)}x{len(embeddings[0]) if embeddings else 0}")
            raise RAGVectorStoreError(
                f"Failed to add chunks to vector store for collection {collection_name}: {exc}", {"collection": collection_name, "details": str(exc)}
            ) from exc

    # -------------------------
    # Query
    # -------------------------
    def _build_filter(self, metadata_filter: Optional[Dict[str, Any]]) -> Optional[Filter]:
        if not metadata_filter:
            return None
        conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in metadata_filter.items()]
        return Filter(must=conditions)

    def query(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, object]]:
        try:
            self.get_or_create_collection(collection_name)

            q_filter = self._build_filter(metadata_filter)

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                query_filter=q_filter,
            )

            formatted: List[Dict[str, object]] = []
            for p in results:
                payload = p.payload or {}
                text = payload.get("text", "")
                meta = {k: v for k, v in payload.items() if k != "text"}
                distance = 1.0 - float(p.score) if p.score is not None else None
                formatted.append({"documents": text, "metadatas": meta, "distances": distance})

            return formatted
        except Exception as exc:
            raise RAGVectorStoreError(
                "Failed to query vector store", {"collection": collection_name}
            ) from exc
