from qdrant_client import QdrantClient

client = QdrantClient(host="qdrant", port=6333)
collection_name = "test_snippet"

# Search without requesting vectors
results = client.search(
    collection_name=collection_name,
    query_vector=[0.01]*384,
    limit=1,
    with_payload=True
)

print("Search results (payload only):", results)

# To see vectors, fetch the point by ID
if results:
    point_id = results[0].id
    point = client.retrieve(
        collection_name=collection_name,
        ids=[point_id]
    )
    print("Full point including vector:", point)

