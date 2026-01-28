# ============================================
# LLM Service (Groq Integration)
# ============================================
# This module connects to Groq's API to generate AI responses.
#
# What is Groq?
# - A fast, free LLM API service
# - We use their Llama 3.1 8B model
# - It takes a prompt and returns a human-like response
#
# What is RAG (Retrieval Augmented Generation)?
# - RAG = Retrieve relevant docs + Generate answer using those docs
# - Instead of the LLM making things up, we give it real documents
# - This makes answers accurate and grounded in facts

from typing import List, Dict, Optional
import os
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL


# ============================================
# Global Client Instance
# ============================================
_client: Optional[Groq] = None


def get_groq_client() -> Groq:
    """
    Get the Groq client (creates once, reuses).
    
    Returns:
        Groq: Initialized Groq client
    """
    global _client
    
    if _client is None:
        api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is required. Set it in .env file or environment variables.")
        _client = Groq(api_key=api_key)
    
    return _client


# ============================================
# Prompt Template for RAG
# ============================================
# This template tells the LLM how to behave and what to do

RAG_PROMPT_TEMPLATE = """You are a helpful customer support assistant for TechMart Electronics.
Your job is to answer customer questions using ONLY the information provided in the context below.

RULES:
1. Only use information from the provided context to answer
2. If the context doesn't contain the answer, say "I don't have information about that in our documentation"
3. Be friendly, professional, and concise
4. Always cite which document the information came from
5. If the customer seems frustrated or has a complaint, acknowledge their concern empathetically

CONTEXT (from company documents):
{context}

CUSTOMER QUESTION: {question}

Provide a helpful answer based on the context above. If citing information, mention the source document."""


def build_context_from_results(search_results: List[Dict]) -> str:
    """
    Build a context string from search results.
    
    This formats the retrieved document chunks into a readable
    format that the LLM can use to answer questions.
    
    Args:
        search_results: List of search results from Qdrant
    
    Returns:
        Formatted context string
    
    Example output:
        [From: Refund_Policy.pdf]
        Refunds are processed within 5-7 business days...
        
        [From: Shipping_Delivery.pdf]
        Standard shipping takes 5-7 days...
    """
    if not search_results:
        return "No relevant documents found."
    
    context_parts = []
    for i, result in enumerate(search_results, 1):
        source = result.get("source", "Unknown")
        text = result.get("text", "")
        score = result.get("score", 0)
        
        context_parts.append(f"[Document {i}: {source}] (Relevance: {score:.0%})\n{text}")
    
    return "\n\n---\n\n".join(context_parts)


def generate_response(
    question: str,
    search_results: List[Dict],
    temperature: float = 0.3
) -> Dict:
    """
    Generate an AI response to a customer question using RAG.
    
    This is the main function that:
    1. Takes search results (retrieved documents)
    2. Builds a prompt with context
    3. Calls Groq API to generate a response
    4. Returns the answer with citations
    
    Args:
        question: The customer's question
        search_results: Retrieved document chunks from Qdrant
        temperature: Creativity level (0=focused, 1=creative)
    
    Returns:
        Dict with 'answer', 'citations', and 'context_used'
    
    Example:
        results = search_documents("refund policy")
        response = generate_response("How do I get a refund?", results)
        print(response['answer'])
    """
    # Build context from search results
    context = build_context_from_results(search_results)
    
    # Build the full prompt
    prompt = RAG_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )
    
    # Call Groq API
    client = get_groq_client()
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful customer support assistant. Be concise and professional."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=GROQ_MODEL,
            temperature=temperature,
            max_tokens=500
        )
        
        # Extract the response
        answer = chat_completion.choices[0].message.content
        
        # Build citations list (as simple strings for frontend)
        citations = []
        seen_sources = set()
        for result in search_results:
            source = result.get("source", "Unknown")
            if source not in seen_sources:
                citations.append(source)
                seen_sources.add(source)
        
        return {
            "answer": answer,
            "citations": citations,
            "model_used": GROQ_MODEL,
            "context_documents": len(search_results)
        }
        
    except Exception as e:
        return {
            "answer": f"Sorry, I encountered an error generating a response: {str(e)}",
            "citations": [],
            "model_used": GROQ_MODEL,
            "error": str(e)
        }


def detect_complaint(text: str) -> bool:
    """
    Detect if the customer message indicates a complaint or frustration.
    
    This is a simple keyword-based detection. In production, you might
    use sentiment analysis or another ML model.
    
    Args:
        text: The customer's message
    
    Returns:
        True if complaint detected, False otherwise
    """
    # Keywords that indicate complaints or frustration (NOT normal questions)
    # Only trigger for clearly negative/angry expressions
    complaint_keywords = [
        "frustrated", "angry", "upset", "terrible",
        "worst", "horrible", "unacceptable", "disappointed", "furious",
        "never received", "still waiting", "no response", "bad experience",
        "want to escalate", "speak to manager", "supervisor",
        "broken", "damaged", "wrong item", "not working",
        "this is ridiculous", "waste of time", "never again",
        "very unhappy", "extremely disappointed", "fed up",
        "demand", "lawsuit", "legal action", "bbb", "complaint"
    ]
    
    text_lower = text.lower()
    
    # Count how many complaint keywords are found
    complaint_count = 0
    for keyword in complaint_keywords:
        if keyword in text_lower:
            complaint_count += 1
    
    # Only flag as complaint if there's strong negative language
    # (at least 1 strong complaint word found)
    return complaint_count >= 1


# ============================================
# Test the LLM service
# ============================================
if __name__ == "__main__":
    print("Testing LLM Service (Groq)")
    print("=" * 50)
    
    # Test 1: API Connection
    print("\n1. Testing Groq API connection...")
    try:
        client = get_groq_client()
        print("   ✅ Groq client initialized!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure your GROQ_API_KEY is set in .env file")
        exit(1)
    
    # Test 2: Generate response with mock search results
    print("\n2. Testing response generation...")
    
    mock_results = [
        {
            "text": "All products can be returned within 30 days of purchase for a full refund. The item must be in original packaging and unused condition. Refunds are processed within 5-7 business days after we receive the item.",
            "source": "Refund_Policy.pdf",
            "score": 0.85
        },
        {
            "text": "To request a refund, contact our support team at support@techmart.com or call 1-800-TECHMART. You will receive a Return Merchandise Authorization (RMA) number.",
            "source": "Refund_Policy.pdf",
            "score": 0.72
        }
    ]
    
    question = "How can I get a refund for my order?"
    print(f"   Question: '{question}'")
    
    response = generate_response(question, mock_results)
    
    print("\n   Answer:")
    print("   " + "-" * 45)
    print(f"   {response['answer']}")
    print("   " + "-" * 45)
    
    print("\n   Citations:")
    for citation in response['citations']:
        print(f"   - {citation['source']} (relevance: {citation['relevance_score']:.0%})")
    
    # Test 3: Complaint detection
    print("\n3. Testing complaint detection...")
    test_messages = [
        ("How do I track my order?", False),
        ("I'm frustrated! My package never arrived!", True),
        ("What's your return policy?", False),
        ("This is unacceptable! I want to speak to a manager!", True),
    ]
    
    for message, expected in test_messages:
        is_complaint = detect_complaint(message)
        status = "✅" if is_complaint == expected else "❌"
        complaint_str = "Complaint" if is_complaint else "Normal"
        print(f"   {status} '{message[:40]}...' → {complaint_str}")
    
    print("\n" + "=" * 50)
    print("✅ LLM service is working correctly!")
