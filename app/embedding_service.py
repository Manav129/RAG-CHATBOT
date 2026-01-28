# ============================================
# Embedding Service
# ============================================
# This module converts text into vectors (embeddings).
# 
# What are embeddings?
# - Text like "I want a refund" becomes an array of 384 numbers
# - Similar texts have similar number patterns
# - This allows us to find related content using math!
#
# Example:
# "I want a refund" → [0.23, -0.45, 0.12, ...]  (384 numbers)
# "Return my money" → [0.25, -0.43, 0.14, ...]  (similar pattern!)
# "Pizza recipe"    → [-0.8, 0.32, -0.56, ...]  (different pattern)

from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION
from typing import List


# ============================================
# Global Model Instance
# ============================================
# We load the model once and reuse it (loading is slow, using is fast)
_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get the embedding model (loads it once, then reuses).
    
    This is called "lazy loading" - we only load when first needed.
    The model is about 90MB and takes a few seconds to load.
    
    Returns:
        SentenceTransformer: The loaded embedding model
    """
    global _model
    
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded successfully!")
    
    return _model


def create_embedding(text: str) -> List[float]:
    """
    Convert a single text into a vector (embedding).
    
    Args:
        text: The text to convert (e.g., "How do I get a refund?")
    
    Returns:
        List of floats representing the text as numbers
        Length is 384 for the all-MiniLM-L6-v2 model
    
    Example:
        >>> embedding = create_embedding("Hello world")
        >>> len(embedding)
        384
    """
    model = get_embedding_model()
    
    # The model returns a numpy array, we convert to list
    embedding = model.encode(text)
    
    return embedding.tolist()


def create_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Convert multiple texts into vectors at once (faster than one by one).
    
    Args:
        texts: List of texts to convert
    
    Returns:
        List of embeddings, one for each input text
    
    Example:
        >>> embeddings = create_embeddings_batch(["Hello", "World"])
        >>> len(embeddings)
        2
        >>> len(embeddings[0])
        384
    """
    model = get_embedding_model()
    
    # Batch processing is more efficient for multiple texts
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Convert numpy arrays to lists
    return [emb.tolist() for emb in embeddings]


def get_embedding_dimension() -> int:
    """
    Get the size of embeddings produced by the model.
    
    Returns:
        int: The dimension of embeddings (384 for our model)
    """
    return EMBEDDING_DIMENSION


# ============================================
# Test the embedding service
# ============================================
if __name__ == "__main__":
    print("Testing Embedding Service")
    print("=" * 50)
    
    # Test single embedding
    test_text = "How can I get a refund for my order?"
    print(f"\nTest text: '{test_text}'")
    
    embedding = create_embedding(test_text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test similarity (similar texts should have similar embeddings)
    print("\n" + "=" * 50)
    print("Testing semantic similarity:")
    
    texts = [
        "I want to return my product",      # Similar to refund
        "How do I get my money back?",       # Similar to refund
        "What are your shipping options?",   # Different topic
    ]
    
    # Get embeddings for all texts
    all_embeddings = create_embeddings_batch([test_text] + texts)
    
    # Calculate cosine similarity (how similar two vectors are)
    import numpy as np
    
    def cosine_similarity(a, b):
        """Calculate similarity between two vectors (0 to 1)."""
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    print(f"\nReference: '{test_text}'")
    print("-" * 50)
    
    for i, text in enumerate(texts):
        similarity = cosine_similarity(all_embeddings[0], all_embeddings[i + 1])
        print(f"Similarity: {similarity:.4f} | '{text}'")
    
    print("\n✅ Embedding service is working correctly!")
    print("Note: Higher similarity = more related topics")
