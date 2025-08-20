from prometheus_client import Counter, Histogram, Gauge

# RAG-specific metrics
rag_queries_total = Counter(
    'rag_queries_total',
    'Total number of RAG queries processed',
    ['collection', 'status']
)

rag_query_duration = Histogram(
    'rag_query_duration_seconds',
    'Time spent processing RAG queries',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

rag_errors_total = Counter(
    'rag_errors_total',
    'Total number of RAG errors',
    ['error_type']
)

vector_operations_total = Counter(
    'vector_operations_total',
    'Total vector database operations',
    ['operation', 'status']
)

embedding_cache_hits = Counter(
    'embedding_cache_hits_total',
    'Number of embedding cache hits'
)

document_chunks_total = Gauge(
    'document_chunks_total',
    'Total number of document chunks in vector store',
    ['collection']
)

