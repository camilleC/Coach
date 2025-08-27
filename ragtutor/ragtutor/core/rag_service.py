# core/rag_service.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import uuid4


from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGBadRequest
from .document_processor import _split_text_with_overlap, process_pdf_document
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
        """Initialize embedding client, vector store, and LLM."""
        self.embedder = EmbeddingClient()

        # ✅ Qdrant vector store (no persist_directory)
        self.vstore = VectorStore()

        self.llm = LLMClient()

        # Auto-load default PDF if available
        await self._load_default_document()

    async def _load_default_document(self) -> None:
        pdf_path = settings.pdf
        if not os.path.exists(pdf_path):
            print(f"ℹ️ No PDF document found at {pdf_path}")
            return

        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            text_pages = 0
            total_chunks = 0

            document_id = str(uuid4())
            all_chunks: list[dict] = []

            print(f"DEBUG: PDF {pdf_path} has {total_pages} pages")

            for page_index, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""

                if not page_text.strip():
                    print(f"DEBUG: Page {page_index} has no extractable text")
                    continue

                text_pages += 1

                chunks = _split_text_with_overlap(
                    page_text, settings.chunk_size, settings.chunk_overlap
                )

                if not chunks:
                    print(
                        f"DEBUG: Page {page_index} text too short for chunking "
                        f"(chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap}). Using full page as one chunk."
                    )
                    chunks = [page_text]

                for chunk_text in chunks:
                    chunk_id = str(uuid4())
                    all_chunks.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "document_id": document_id,
                            "filename": os.path.basename(pdf_path),
                            "page": page_index,
                        },
                    })

                total_chunks += len(chunks)

            if not all_chunks:
                print(f"⚠️ Loaded PDF but no text chunks could be created")
            else:
                # Add all chunks to your vector store
                self.vstore.add_chunks(settings.collection_name, all_chunks, self.embedder.embed([c["text"] for c in all_chunks]))
                print(f"✅ Loaded PDF {pdf_path} ({text_pages}/{total_pages} pages with text), total chunks: {total_chunks}")

        except Exception as e:
            print(f"⚠️ Failed to load PDF {pdf_path}: {e}")

    async def cleanup(self) -> None:
        """Optional cleanup logic for service shutdown."""
        pass

    async def ingest_document(
        self,
        filename: str,
        content: bytes,
        collection_name: Optional[str]
    ) -> Dict[str, object]:
        """Ingest a PDF into the vector store with safety checks."""
        if not filename.lower().endswith(".pdf"):
            raise RAGBadRequest("Only PDF files are supported")

        collection = collection_name or settings.collection_name
        processed = process_pdf_document(filename, content)
        chunks = processed.get("chunks", [])

        if not chunks:
            print(f"⚠️ No chunks extracted from '{filename}'")
            return {"document_id": processed["document_id"], "chunks_created": 0}

        texts = [c.get("text", "") for c in chunks]

        # Generate embeddings
        try:
            embeddings = self.embedder.embed(texts)
        except Exception as e:
            print(f"⚠️ Failed to generate embeddings for '{filename}': {e}")
            return {"document_id": processed["document_id"], "chunks_created": 0}

        # Validate length
        if len(chunks) != len(embeddings):
            print(
                f"⚠️ Chunk/embedding length mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings"
            )
            return {"document_id": processed["document_id"], "chunks_created": 0}

        # Attempt to add to vector store
        try:
            self.vstore.add_chunks(collection, chunks, embeddings)
        except Exception as e:
            print(f"⚠️ Failed to add chunks to vector store '{collection}': {e}")
            return {"document_id": processed["document_id"], "chunks_created": 0}

        return {"document_id": processed["document_id"], "chunks_created": len(chunks)}

    async def query(
        self,
        query: str,
        top_k: int,
        collection_name: Optional[str]
    ) -> Dict[str, object]:
        """Run a semantic search query and return LLM response + sources."""
        if not query.strip():
            raise RAGBadRequest("Query cannot be empty")

        collection = collection_name or settings.collection_name
        q_embed = self.embedder.embed([query])[0]
        results = self.vstore.query(collection, q_embed, top_k)

        sources: List[Dict[str, object]] = []
        for result in results:
            sources.append({
                "text": result.get("documents", ""),
                "metadata": result.get("metadatas", {}),
                "confidence_score": float(max(0.0, 1.0 - result.get("distances", 0.0))),
            })

        # Context to feed into LLM
        context_parts = [
            f"[p{s['metadata'].get('page','?')}] {s['text']}"
            for s in sources[:5]
        ]
        context = "\n\n".join(context_parts)

        prompt = (
            "You are an expert coach. Answer based only on the context.\n"
            "If the answer cannot be found in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        )

        answer = self.llm.chat(prompt)

        confidence = float(
            sum(s["confidence_score"] for s in sources) / max(1, len(sources))
        )

        return {
            "answer": answer,
            "sources": sources,
            "confidence_score": confidence,
        }

    async def list_collections(self) -> List[str]:
        """Return all collections from vector store."""
        return self.vstore.list_collections()
