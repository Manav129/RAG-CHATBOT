# ============================================
# FastAPI Main Application
# ============================================
# This is the main entry point for our API server.
#
# Endpoints:
# - POST /ingest      → Index PDFs into vector database
# - POST /chat        → Chat with the AI assistant
# - POST /tickets     → Create a ticket manually
# - GET  /tickets     → List all tickets
# - GET  /tickets/{id}→ Get a specific ticket
# - PATCH /tickets/{id} → Update ticket status
# - GET  /health      → Health check
# - GET  /stats       → System statistics

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os


# ============================================
# Initialize FastAPI App
# ============================================
app = FastAPI(
    title="AI Customer Support Agent",
    description="""
    🤖 An intelligent customer support chatbot powered by RAG (Retrieval Augmented Generation).
    
    Features:
    - Answer questions using company documents
    - Provide citations for answers
    - Automatically create tickets for complaints
    - Track and manage support tickets
    """,
    version="1.0.0",
    docs_url="/docs",      # Swagger UI at /docs
    redoc_url="/redoc"     # ReDoc at /redoc
)


# ============================================
# CORS Configuration
# ============================================
# This allows our frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)


# ============================================
# Startup Event
# ============================================
@app.on_event("startup")
async def startup_event():
    """Run when the server starts."""
    print("\nStarting server...")
    
    # Import and create database tables
    print("Initializing database...")
    try:
        from app.models import create_tables
        create_tables()
    except Exception as e:
        print(f"Warning: {e}")
    
    print("Server ready.")
    print("API docs: http://localhost:8001/docs\n")


# ============================================
# Request/Response Models (Pydantic)
# ============================================
# These define the structure of data sent to/from the API

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    query: str = Field(..., description="The customer's question", min_length=1)
    customer_email: Optional[str] = Field(None, description="Customer email for ticket creation")
    customer_name: Optional[str] = Field(None, description="Customer name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I get a refund for my order?",
                "customer_email": "customer@example.com",
                "customer_name": "John Doe"
            }
        }


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    query: str
    answer: str
    citations: List[str]  # List of source document names
    is_complaint: bool
    ticket_id: Optional[str] = None
    ticket_created: bool = False


class TicketCreateRequest(BaseModel):
    """Request body for creating a ticket manually."""
    customer_query: str = Field(..., description="Customer's issue description")
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    priority: str = Field("medium", description="Priority: low, medium, high, urgent")
    category: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_query": "I need help with my order",
                "customer_email": "customer@example.com",
                "priority": "medium"
            }
        }


class TicketUpdateRequest(BaseModel):
    """Request body for updating a ticket."""
    status: str = Field(..., description="New status: open, in_progress, resolved, closed")
    notes: Optional[str] = Field(None, description="Additional notes")


class IngestRequest(BaseModel):
    """Request body for document ingestion."""
    reset: bool = Field(False, description="If true, delete existing data and re-index")


# ============================================
# Health Check Endpoint
# ============================================
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the system.
    Use this to verify the API is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Customer Support Agent"
    }


# ============================================
# Statistics Endpoint
# ============================================
@app.get("/stats", tags=["System"])
async def get_stats():
    """
    Get system statistics.
    
    Returns information about:
    - Number of documents indexed
    - Ticket counts by status
    """
    from app.rag_pipeline import get_system_status
    from app.ticket_service import get_ticket_stats
    
    # Get RAG system status
    rag_status = get_system_status()
    
    # Get ticket statistics
    ticket_stats = get_ticket_stats()
    
    return {
        "rag_system": rag_status,
        "tickets": ticket_stats,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# Document Ingestion Endpoint
# ============================================
@app.post("/ingest", tags=["Documents"])
async def ingest_docs(request: IngestRequest = None):
    """
    Ingest PDF documents into the vector database.
    
    This processes all PDFs in the data/docs folder and indexes them
    for semantic search. Run this when you add or update documents.
    
    - **reset**: If true, deletes existing data and re-indexes everything
    """
    from app.rag_pipeline import ingest_documents
    
    reset = request.reset if request else False
    
    try:
        result = ingest_documents(reset=reset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Chat Endpoint (Main RAG Pipeline)
# ============================================
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the AI customer support assistant.
    
    This endpoint:
    1. Searches for relevant documents
    2. Generates an AI response with citations
    3. Detects if it's a complaint
    4. Automatically creates a ticket for complaints
    
    Returns the answer, citations, and ticket ID if created.
    """
    from app.rag_pipeline import chat
    from app.ticket_service import create_ticket
    
    try:
        # Run the RAG pipeline
        response = chat(request.query)
        
        ticket_id = None
        ticket_created = False
        
        # Auto-create ticket for complaints
        if response.get("should_create_ticket", False):
            ticket_result = create_ticket(
                customer_query=request.query,
                ai_response=response.get("answer", ""),
                customer_email=request.customer_email,
                customer_name=request.customer_name,
                priority="high",  # Complaints get high priority
                category="complaint"
            )
            
            if ticket_result.get("success"):
                ticket_id = ticket_result["ticket"]["ticket_id"]
                ticket_created = True
        
        return ChatResponse(
            query=request.query,
            answer=response.get("answer", ""),
            citations=response.get("citations", []),
            is_complaint=response.get("is_complaint", False),
            ticket_id=ticket_id,
            ticket_created=ticket_created
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Ticket Endpoints
# ============================================

@app.post("/tickets", tags=["Tickets"])
async def create_new_ticket(request: TicketCreateRequest):
    """
    Create a new support ticket manually.
    
    Use this when you want to create a ticket without going through the chat.
    """
    from app.ticket_service import create_ticket
    
    result = create_ticket(
        customer_query=request.customer_query,
        customer_email=request.customer_email,
        customer_name=request.customer_name,
        priority=request.priority,
        category=request.category
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create ticket"))
    
    return result


@app.get("/tickets", tags=["Tickets"])
async def list_all_tickets(status: Optional[str] = None, limit: int = 50):
    """
    List all tickets.
    
    - **status**: Filter by status (open, in_progress, resolved, closed)
    - **limit**: Maximum number of tickets to return (default: 50)
    """
    from app.ticket_service import list_tickets
    
    tickets = list_tickets(status=status, limit=limit)
    return {
        "count": len(tickets),
        "tickets": tickets
    }


@app.get("/tickets/{ticket_id}", tags=["Tickets"])
async def get_ticket_by_id(ticket_id: str):
    """
    Get a specific ticket by its ID.
    
    - **ticket_id**: The ticket ID (e.g., TKT-00001)
    """
    from app.ticket_service import get_ticket
    
    ticket = get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    return ticket


@app.patch("/tickets/{ticket_id}", tags=["Tickets"])
async def update_ticket(ticket_id: str, request: TicketUpdateRequest):
    """
    Update a ticket's status.
    
    - **ticket_id**: The ticket ID to update
    - **status**: New status (open, in_progress, resolved, closed)
    - **notes**: Optional notes about the update
    """
    from app.ticket_service import update_ticket_status
    
    result = update_ticket_status(
        ticket_id=ticket_id,
        status=request.status,
        notes=request.notes
    )
    
    if not result.get("success"):
        if "not found" in result.get("error", "").lower():
            raise HTTPException(status_code=404, detail=result.get("error"))
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


# ============================================
# Serve Frontend Static Files
# ============================================
# This serves our HTML/CSS/JS frontend
# The frontend folder contains: index.html, style.css, script.js

frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/", tags=["Frontend"])
async def serve_frontend():
    """Serve the main frontend page."""
    return FileResponse(os.path.join(frontend_folder, "index.html"))

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=frontend_folder), name="static")


# ============================================
# Run the server (for development)
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
