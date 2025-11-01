import os
import pytest
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance


@pytest.fixture
def qdrant_client():
    """Create Qdrant client."""
    host = os.getenv("VECTOR_DB_HOST", "localhost")
    port = int(os.getenv("VECTOR_DB_PORT", "6333"))
    return QdrantClient(host=host, port=port)


@pytest.fixture
def collection_name():
    return "test_snippet"


def test_qdrant_collection_exists(qdrant_client, collection_name):
    """Test that collection can be created or retrieved."""
    try:
        qdrant_client.get_collection(collection_name=collection_name)
    except Exception:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    
    # Verify collection exists
    collection_info = qdrant_client.get_collection(collection_name=collection_name)
    assert collection_info is not None


def test_qdrant_search(qdrant_client, collection_name):
    """Test searching in Qdrant collection."""
    # Ensure collection exists
    try:
        qdrant_client.get_collection(collection_name=collection_name)
    except Exception:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

    # Search without requesting vectors
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=[0.01]*384,
        limit=1,
        with_payload=True
    )

    print("Search results (payload only):", results)
    assert isinstance(results, list)

    # To see vectors, fetch the point by ID if results exist
    if results:
        point_id = results[0].id
        point = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[point_id]
        )
        print("Full point including vector:", point)
        assert point is not None

