import os
from coach.core.document_processor import process_pdf_document
from coach.core.embeddings import EmbeddingClient
from coach.core.vector_store import VectorStore
from coach.config.settings import settings

PDF_PATH = "./data/coaching.pdf"
COLLECTION = settings.collection_name

# 1️⃣ Load PDF
if not os.path.exists(PDF_PATH):
    print(f"PDF not found at {PDF_PATH}")
    exit(1)

with open(PDF_PATH, "rb") as f:
    content = f.read()

# 2️⃣ Process PDF into chunks
result = process_pdf_document("coaching.pdf", content)
chunks = result["chunks"]
print(f"Document ID: {result['document_id']}")
print(f"Total chunks created: {len(chunks)}")

if not chunks:
    print("No chunks created. Check PDF text extraction or split function.")
    exit(1)

# 3️⃣ Generate embeddings
embedder = EmbeddingClient()
texts = [c["text"] for c in chunks]

try:
    embeddings = embedder.embed(texts)
    print(f"Generated embeddings for {len(embeddings)} chunks")
except Exception as e:
    print(f"Embedding generation failed: {e}")
    exit(1)

# 4️⃣ Add chunks + embeddings to vector store
vstore = VectorStore()
try:
    vstore.add_chunks(COLLECTION, chunks, embeddings)
    print(f"Added {len(chunks)} chunks to vector store '{COLLECTION}'")
except Exception as e:
    print(f"Failed to add chunks to vector store '{COLLECTION}': {e}")
    exit(1)

# 5️⃣ Test a sample query
sample_query = "What is the main coaching goal?"
query_embedding = embedder.embed([sample_query])[0]

try:
    results = vstore.query(COLLECTION, query_embedding, top_k=5)
    print(f"Sample query returned {len(results)} results")
    for r in results[:3]:
        print(f"- {r['documents'][:100]}... (page: {r['metadatas'].get('page','?')})")
except Exception as e:
    print(f"Query failed: {e}")

