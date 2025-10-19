from qdrant_client import QdrantClient

# -----------------------
# Connection
# -----------------------
client = QdrantClient(host='qdrant', port=6333)

# -----------------------
# Settings
# -----------------------
collection_name = 'documents'
dim = 384

# -----------------------
# Delete old collection if exists
# -----------------------
existing_collections = [c.name for c in client.get_collections().collections]
if collection_name in existing_collections:
    client.delete_collection(collection_name)
    print(f'Deleted old collection: {collection_name}')

# -----------------------
# Create new collection
# -----------------------
client.create_collection(
    collection_name=collection_name,
    vectors_config={'size': dim, 'distance': 'Cosine'}
)
print(f'Created collection {collection_name} with dim={dim}')

# -----------------------
# Insert a test point
# -----------------------
client.upsert(
    collection_name=collection_name,
    points=[{'id': 1, 'vector': [0.01]*dim, 'payload': {'text': 'Hello embedding'}}]
)
print('Inserted 1 test point')

# -----------------------
# Search test
# -----------------------
results = client.search(
    collection_name=collection_name,
    query_vector=[0.01]*dim,
    limit=1,
    with_payload=True
)
print('Search results:', results)

