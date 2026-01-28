# ============================================
# Qdrant Vector Database Service
# ============================================
# This module handles all interactions with Qdrant vector database.
#
# What is Qdrant?
# - A vector database that stores embeddings (arrays of numbers)
# - Enables "semantic search" - finding similar content by meaning
# - Much faster than comparing every document manually
#
# How it works:
# 1. Store: Document chunk + its embedding → Qdrant
# 2. Search: Query embedding → Qdrant finds most similar stored embeddings
# 3. Return: The original text chunks that match the query

from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_DIMENSION
)
from app.embedding_service import create_embedding, create_embeddings_batch


# ============================================
# Global Client Instance
# ============================================
_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """
    Get the Qdrant client (creates connection once, reuses it).
    
    Supports both local storage and Qdrant Cloud.
    
    Returns:
        QdrantClient: Connected client to Qdrant database
    """
    global _client
    
    if _client is None:
        if QDRANT_API_KEY:
            # Use Qdrant Cloud with API key
            print(f"Connecting to Qdrant Cloud at {QDRANT_URL}...")
            _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            print("Connected to Qdrant Cloud!")
        elif QDRANT_URL.startswith("http"):
            # Use remote Qdrant without API key
            print(f"Connecting to Qdrant at {QDRANT_URL}...")
            _client = QdrantClient(url=QDRANT_URL)
            print("Connected to Qdrant!")
        else:
            # Use local file-based storage (development mode)
            print("Using Qdrant with local storage (qdrant_data folder)...")
            _client = QdrantClient(path="./qdrant_data")
            print("Qdrant client initialized with local storage!")
    
    return _client


def create_collection(collection_name: str = QDRANT_COLLECTION) -> bool:
    """
    Create a collection (like a table) in Qdrant if it doesn't exist.
    
    A collection stores vectors of a specific size. Our embeddings
    are 384-dimensional, so we create a collection that accepts 384-D vectors.
    
    Args:
        collection_name: Name for the collection (default: from config)
    
    Returns:
        True if created or already exists, False on error
    """
    client = get_qdrant_client()
    
    # Check if collection already exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if collection_name in collection_names:
        print(f"Collection '{collection_name}' already exists.")
        return True
    
    # Create new collection
    print(f"Creating collection '{collection_name}'...")
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSION,   # 384 for our model
            distance=Distance.COSINE    # Use cosine similarity for comparison
        )
    )
    
    print(f"Collection '{collection_name}' created successfully!")
    return True


def delete_collection(collection_name: str = QDRANT_COLLECTION) -> bool:
    """
    Delete a collection (useful for re-indexing all documents).
    
    Args:
        collection_name: Name of collection to delete
    
    Returns:
        True if deleted, False if didn't exist
    """
    client = get_qdrant_client()
    
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' deleted.")
        return True
    except Exception as e:
        print(f"Collection '{collection_name}' doesn't exist or error: {e}")
        return False


def store_documents(
    chunks: List[Dict],
    collection_name: str = QDRANT_COLLECTION
) -> int:
    """
    Store document chunks in Qdrant with their embeddings.
    
    This is the "indexing" step - we convert each chunk to an embedding
    and store it in Qdrant for later searching.
    
    Args:
        chunks: List of dicts with 'text' and 'metadata' keys
        collection_name: Qdrant collection to store in
    
    Returns:
        Number of documents stored
    
    Example:
        chunks = [
            {'text': 'Refund policy...', 'metadata': {'source': 'refund.pdf'}},
            ...
        ]
        count = store_documents(chunks)
    """
    if not chunks:
        print("No chunks to store!")
        return 0
    
    client = get_qdrant_client()
    
    # Ensure collection exists
    create_collection(collection_name)
    
    # Extract texts for batch embedding
    texts = [chunk["text"] for chunk in chunks]
    
    print(f"Creating embeddings for {len(texts)} chunks...")
    embeddings = create_embeddings_batch(texts)
    
    # Create points (Qdrant's term for stored items)
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point = PointStruct(
            id=i,                           # Unique ID for this point
            vector=embedding,               # The 384-D embedding
            payload={                       # Metadata (stored alongside vector)
                "text": chunk["text"],
                "source": chunk["metadata"]["source"],
                "chunk_index": chunk["metadata"]["chunk_index"],
            }
        )
        points.append(point)
    
    # Upload to Qdrant in batches
    print(f"Uploading {len(points)} points to Qdrant...")
    
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )
    
    print(f"Successfully stored {len(points)} documents!")
    return len(points)


def search_documents(
    query: str,
    top_k: int = 3,
    collection_name: str = QDRANT_COLLECTION
) -> List[Dict]:
    """
    Search for documents similar to the query.
    
    This is the "retrieval" step of RAG:
    1. Convert query to embedding
    2. Find most similar embeddings in Qdrant
    3. Return the original text chunks
    
    Args:
        query: The search query (e.g., "How do I get a refund?")
        top_k: Number of results to return (default: 3)
        collection_name: Qdrant collection to search
    
    Returns:
        List of dicts with 'text', 'source', 'score' keys
    
    Example:
        results = search_documents("refund policy")
        for r in results:
            print(f"Source: {r['source']}, Score: {r['score']:.2f}")
            print(f"Text: {r['text'][:100]}...")
    """
    client = get_qdrant_client()
    
    # Convert query to embedding
    query_embedding = create_embedding(query)
    
    # Search in Qdrant
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k
    )
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "text": result.payload["text"],
            "source": result.payload["source"],
            "chunk_index": result.payload["chunk_index"],
            "score": result.score  # Similarity score (0-1, higher = more similar)
        })
    
    return formatted_results


def get_collection_info(collection_name: str = QDRANT_COLLECTION) -> Dict:
    """
    Get information about a collection (number of documents, etc.).
    
    Returns:
        Dict with collection stats
    """
    client = get_qdrant_client()
    
    try:
        info = client.get_collection(collection_name=collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================
# Test the Qdrant service
# ============================================
if __name__ == "__main__":
    print("Testing Qdrant Service")
    print("=" * 50)
    
    # Test connection
    print("\n1. Testing connection...")
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        print(f"   Connected! Found {len(collections.collections)} existing collections.")
    except Exception as e:
        print(f"   ERROR: Could not connect to Qdrant!")
        print(f"   Make sure Qdrant is running: docker-compose up -d")
        print(f"   Error details: {e}")
        exit(1)
    
    # Test collection creation
    print("\n2. Creating test collection...")
    create_collection("test_collection")
    
    # Test storing documents
    print("\n3. Storing test documents...")
    test_chunks = [
        {"text": "Our refund policy allows returns within 30 days.", 
         "metadata": {"source": "refund.pdf", "chunk_index": 0}},
        {"text": "Shipping takes 5-7 business days for standard delivery.", 
         "metadata": {"source": "shipping.pdf", "chunk_index": 0}},
        {"text": "Contact support at support@example.com for help.", 
         "metadata": {"source": "support.pdf", "chunk_index": 0}},
    ]
    store_documents(test_chunks, "test_collection")
    
    # Test searching
    print("\n4. Testing search...")
    query = "How can I return a product?"
    print(f"   Query: '{query}'")
    results = search_documents(query, top_k=2, collection_name="test_collection")
    
    print("\n   Results:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['score']:.4f} | Source: {result['source']}")
        print(f"      Text: {result['text']}")
    
    # Cleanup test collection
    print("\n5. Cleaning up test collection...")
    delete_collection("test_collection")
    
    print("\n" + "=" * 50)
    print("✅ Qdrant service is working correctly!")
