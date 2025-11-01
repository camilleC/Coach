# test_vector_store.py
import os
import pytest
from uuid import uuid4
from pypdf import PdfReader

from coach.config.settings import settings
from coach.core.document_processor import _split_text_with_overlap
from coach.core.embeddings import EmbeddingClient
from coach.core.vector_store import VectorStore


@pytest.fixture
def embedder():
    return EmbeddingClient()


@pytest.fixture
def vstore():
    return VectorStore()


@pytest.fixture
def pdf_chunks():
    """Load and chunk PDF for testing."""
    pdf_path = settings.pdf
    if not os.path.exists(pdf_path):
        pytest.skip(f"PDF not found at {pdf_path}")

    reader = PdfReader(pdf_path)
    all_chunks = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue

        chunks = _split_text_with_overlap(text, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            chunks = [text]

        for chunk_text in chunks:
            all_chunks.append({
                "id": str(uuid4()),
                "text": chunk_text,
                "metadata": {
                    "filename": os.path.basename(pdf_path),
                    "page": page_index,
                },
            })

    if not all_chunks:
        pytest.skip("No chunks were created. PDF may be scanned or empty.")

    return all_chunks


def test_vector_store_ingestion(embedder, vstore, pdf_chunks):
    """Test adding chunks to vector store."""
    collection_name = settings.collection_name
    texts = [c["text"] for c in pdf_chunks]
    embeddings = embedder.embed(texts)

    assert len(embeddings) == len(pdf_chunks), "Embeddings count mismatch"

    vstore.add_chunks(collection_name, pdf_chunks, embeddings)
    print(f"✅ Added {len(pdf_chunks)} chunks to collection '{collection_name}'")


def test_vector_store_query(embedder, vstore, pdf_chunks):
    """Test querying the vector store."""
    collection_name = settings.collection_name

    # First, ensure chunks are ingested
    texts = [c["text"] for c in pdf_chunks]
    embeddings = embedder.embed(texts)
    vstore.add_chunks(collection_name, pdf_chunks, embeddings)

    # Now test query
    query_text = "What is the coaching approach?"
    q_embed = embedder.embed([query_text])[0]
    results = vstore.query(collection_name, q_embed, top_k=5)

    assert len(results) > 0, "Query should return results"
    print(f"✅ Sample query returned {len(results)} results")

