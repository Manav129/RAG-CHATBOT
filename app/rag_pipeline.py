# ============================================
# RAG Pipeline Service
# ============================================
# This module combines all services into one unified pipeline.
#
# The RAG Pipeline does:
# 1. INGEST: Load PDFs → Create chunks → Store in Qdrant
# 2. CHAT: Query → Search Qdrant → Generate response with LLM
#
# This is the "brain" of our customer support chatbot!

from typing import Dict, List, Optional
from app.pdf_service import process_all_pdfs
from app.qdrant_service import (
    store_documents,
    search_documents,
    delete_collection,
    get_collection_info,
    create_collection
)
from app.llm_service import generate_response, detect_complaint
from app.config import QDRANT_COLLECTION, TOP_K_RESULTS


# ============================================
# INGEST PIPELINE
# ============================================
# This is run once (or when documents change) to index all PDFs


def ingest_documents(reset: bool = False) -> Dict:
    """
    Ingest all PDF documents into the vector database.
    
    This is the "indexing" step that needs to run before chat works.
    It processes all PDFs in data/docs/ and stores them in Qdrant.
    
    Args:
        reset: If True, delete existing data and re-index everything
    
    Returns:
        Dict with status and statistics
    
    Example:
        result = ingest_documents(reset=True)
        print(f"Indexed {result['documents_stored']} chunks")
    """
    print("\nDocument Ingestion Pipeline")
    
    # Step 1: Optionally reset the collection
    if reset:
        print("Resetting collection...")
        delete_collection(QDRANT_COLLECTION)
        create_collection(QDRANT_COLLECTION)
    else:
        print("Checking collection...")
        create_collection(QDRANT_COLLECTION)
    
    # Step 2: Process all PDFs
    print("Processing PDF documents...")
    chunks = process_all_pdfs()
    
    if not chunks:
        return {
            "status": "error",
            "message": "No documents found to process",
            "documents_stored": 0
        }
    
    # Step 3: Store in Qdrant (embeddings are created automatically)
    print("Storing documents in vector database...")
    stored_count = store_documents(chunks)
    
    # Step 4: Get collection info
    print("Verifying storage...")
    collection_info = get_collection_info()
    
    print("Ingestion complete.\n")
    
    return {
        "status": "success",
        "message": "Documents ingested successfully",
        "documents_stored": stored_count,
        "collection_info": collection_info
    }


# ============================================
# CHAT PIPELINE
# ============================================
# This handles user queries and generates responses


def chat(query: str, top_k: int = TOP_K_RESULTS) -> Dict:
    """
    Process a customer query and generate a response.
    
    This is the main RAG pipeline:
    1. Search for relevant documents
    2. Generate response using LLM + context
    3. Detect if it's a complaint
    4. Return answer with citations
    
    Args:
        query: The customer's question
        top_k: Number of documents to retrieve (default: 3)
    
    Returns:
        Dict with answer, citations, is_complaint flag
    
    Example:
        response = chat("How do I get a refund?")
        print(response['answer'])
        print(response['citations'])
    """
    # Step 1: Search for relevant documents
    search_results = search_documents(query, top_k=top_k)
    
    if not search_results:
        return {
            "query": query,
            "answer": "I'm sorry, but I couldn't find any relevant information in our documentation. Please contact our support team at support@goelelectronics.com for assistance.",
            "citations": [],
            "is_complaint": False,
            "should_create_ticket": False
        }
    
    # Step 2: Generate response using LLM
    llm_response = generate_response(query, search_results)
    
    # Step 3: Check if it's a complaint
    is_complaint = detect_complaint(query)
    
    # Step 4: Prepare final response
    response = {
        "query": query,
        "answer": llm_response["answer"],
        "citations": llm_response["citations"],
        "is_complaint": is_complaint,
        "should_create_ticket": is_complaint,  # Auto-create ticket for complaints
        "model_used": llm_response.get("model_used", "unknown")
    }
    
    return response


def get_system_status() -> Dict:
    """
    Get the current status of the RAG system.
    
    Returns:
        Dict with system status information
    """
    collection_info = get_collection_info()
    
    return {
        "status": "operational",
        "collection": QDRANT_COLLECTION,
        "documents_indexed": collection_info.get("points_count", 0),
        "vector_count": collection_info.get("vectors_count", 0),
    }


# ============================================
# Test the RAG Pipeline
# ============================================
if __name__ == "__main__":
    print("Testing RAG Pipeline")
    print("=" * 60)
    
    # Test 1: Check system status
    print("\n1. Checking system status...")
    status = get_system_status()
    print(f"   Status: {status['status']}")
    print(f"   Documents indexed: {status['documents_indexed']}")
    
    # Test 2: Ingest documents if not already done
    if status['documents_indexed'] == 0:
        print("\n2. No documents found. Running ingestion...")
        ingest_result = ingest_documents(reset=True)
        print(f"   Result: {ingest_result['status']}")
        print(f"   Documents stored: {ingest_result['documents_stored']}")
    else:
        print(f"\n2. Documents already indexed: {status['documents_indexed']} chunks")
    
    # Test 3: Test chat with various queries
    print("\n3. Testing chat pipeline with sample queries...")
    
    test_queries = [
        "What is your refund policy?",
        "How long does shipping take?",
        "I'm frustrated! My order never arrived and no one is helping me!",
        "How do I reset my password?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST QUERY {i}: {query}")
        print("=" * 60)
        
        response = chat(query)
        
        print(f"\n📝 ANSWER:")
        print("-" * 40)
        print(response['answer'])
        print("-" * 40)
        
        print(f"\n📚 CITATIONS:")
        for citation in response['citations']:
            print(f"   - {citation['source']} ({citation['relevance_score']:.0%})")
        
        if response['is_complaint']:
            print(f"\n⚠️ COMPLAINT DETECTED - Should create ticket: {response['should_create_ticket']}")
    
    print("\n" + "=" * 60)
    print("✅ RAG Pipeline test complete!")
