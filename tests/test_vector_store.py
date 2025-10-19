# test_vector_store.py
import os
from uuid import uuid4
from pypdf import PdfReader

from core.config.settings import settings
from core.rag_service import _split_text_with_overlap
from core.embeddings import EmbeddingClient
from core.vector_store import VectorStore

# ===== Initialize embedder and vector store =====
embedder = EmbeddingClient()
vstore = VectorStore()
collection_name = settings.collection_name

# ===== Load PDF =====
pdf_path = settings.pdf
if not os.path.exists(pdf_path):
    print(f"❌ PDF not found at {pdf_path}")
    exit(1)

reader = PdfReader(pdf_path)
all_chunks = []

# ===== Extract text and create chunks =====
for page_index, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    if not text.strip():
        print(f"DEBUG: Page {page_index} has no extractable text")
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

print(f"DEBUG: Total chunks created: {len(all_chunks)}")

if not all_chunks:
    print("❌ No chunks were created. PDF may be scanned or empty.")
    exit(1)

# ===== Generate embeddings =====
texts = [c["text"] for c in all_chunks]
embeddings = embedder.embed(texts)
print(f"DEBUG: Generated {len(embeddings)} embeddings")

# ===== Add to vector store =====
try:
    vstore.add_chunks(collection_name, all_chunks, embeddings)
    print(f"✅ Added {len(all_chunks)} chunks to collection '{collection_name}'")
except Exception as e:
    print(f"❌ Failed to add chunks to vector store: {e}")

# ===== Optional: test a query =====
try:
    query_text = "What is the coaching approach?"
    q_embed = embedder.embed([query_text])[0]
    results = vstore.query(collection_name, q_embed, top_k=5)
    print(f"✅ Sample query returned {len(results)} results")
    for i, r in enumerate(results, 1):
        print(f"{i}. Page {r.get('metadatas', {}).get('page','?')}: {r.get('documents','')[:200]}...")
except Exception as e:
    print(f"❌ Query test failed: {e}")

