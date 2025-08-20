from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGBadRequest
from .document_processor import process_pdf_document
from .embeddings import EmbeddingClient
from .vector_store import VectorStore
from .llm_client import LLMClient


@dataclass
class QueryResult:
    answer: str
    sources: List[Dict[str, object]]
    confidence_score: float


class RAGService:
    def __init__(self):
        self.embedder: Optional[EmbeddingClient] = None
        self.vstore: Optional[VectorStore] = None
        self.llm: Optional[LLMClient] = None

    async def initialize(self) -> None:
        self.embedder = EmbeddingClient()
        self.vstore = VectorStore()
        self.llm = LLMClient()

    async def cleanup(self) -> None:
        # Chroma client does not require explicit close; leave hook for future resources
        pass

    async def ingest_document(self, filename: str, content: bytes, collection_name: Optional[str]) -> Dict[str, object]:
        if not filename.lower().endswith('.pdf'):
            raise RAGBadRequest("Only PDF files are supported")
        collection = collection_name or settings.collection_name
        processed = process_pdf_document(filename, content)
        chunks = processed["chunks"]
        if not chunks:
            return {"document_id": processed["document_id"], "chunks_created": 0}
        texts = [c["text"] for c in chunks]
        embeddings = self.embedder.embed(texts)
        self.vstore.add_chunks(collection, chunks, embeddings)
        return {"document_id": processed["document_id"], "chunks_created": len(chunks)}

    async def query(self, query: str, top_k: int, collection_name: Optional[str]) -> Dict[str, object]:
        if not query.strip():
            raise RAGBadRequest("Query cannot be empty")
        collection = collection_name or settings.collection_name
        q_embed = self.embedder.embed([query])[0]
        results = self.vstore.query(collection, q_embed, top_k)

        documents: List[str] = results.get("documents", [[]])[0]
        metadatas: List[Dict[str, object]] = results.get("metadatas", [[]])[0]
        distances: List[float] = results.get("distances", [[]])[0]

        sources: List[Dict[str, object]] = []
        for text, meta, dist in zip(documents, metadatas, distances):
            sources.append({"text": text, "metadata": meta, "confidence_score": float(max(0.0, 1.0 - (dist or 0.0)))})

        context_parts = []
        for s in sources[:5]:
            context_parts.append(f"[p{ s['metadata'].get('page','?') }] {s['text']}")
        context = "\n\n".join(context_parts)

        prompt = (
            "You are an expert assistant that answers based only on the context.\n"
            "If the answer cannot be found in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        )
        answer = self.llm.chat(prompt)

        confidence = float(sum(s["confidence_score"] for s in sources) / max(1, len(sources)))
        return {"answer": answer, "sources": sources, "confidence_score": confidence}

    async def list_collections(self) -> List[str]:
        return self.vstore.list_collections()


