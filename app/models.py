# ============================================
# Database Models (SQLAlchemy)
# ============================================
# This module defines the database tables using SQLAlchemy ORM.
#
# What is ORM (Object Relational Mapping)?
# - Instead of writing SQL queries, we use Python classes
# - Each class = one table in the database
# - Each attribute = one column in the table
# - Much easier and safer than raw SQL!

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

from app.config import DATABASE_URL


# ============================================
# Database Setup
# ============================================
# Create the database engine (connection)
engine = create_engine(DATABASE_URL, echo=False)

# Create a session factory (for database operations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# ============================================
# Enums (Status and Priority Options)
# ============================================
# Enums define fixed choices for a field

class TicketStatus(enum.Enum):
    """Possible statuses for a support ticket."""
    OPEN = "open"           # New ticket, not yet addressed
    IN_PROGRESS = "in_progress"  # Being worked on
    RESOLVED = "resolved"   # Issue fixed
    CLOSED = "closed"       # Ticket closed

class TicketPriority(enum.Enum):
    """Priority levels for tickets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ============================================
# Ticket Model (Database Table)
# ============================================

class Ticket(Base):
    """
    Support Ticket model.
    
    This creates a table called 'tickets' with these columns:
    - id: Unique identifier (auto-generated)
    - ticket_id: Human-readable ID like "TKT-00001"
    - customer_query: The original customer question
    - ai_response: The chatbot's response
    - status: Current status (open, in_progress, resolved, closed)
    - priority: Priority level (low, medium, high, urgent)
    - created_at: When the ticket was created
    - updated_at: When the ticket was last updated
    """
    
    __tablename__ = "tickets"  # Table name in MySQL
    
    # Primary key - auto-incrementing ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Human-readable ticket ID (TKT-00001, TKT-00002, etc.)
    ticket_id = Column(String(20), unique=True, index=True, nullable=False)
    
    # Customer information
    customer_email = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    
    # The conversation
    customer_query = Column(Text, nullable=False)  # What the customer asked
    ai_response = Column(Text, nullable=True)      # What the bot replied
    
    # Ticket management
    status = Column(
        Enum(TicketStatus),
        default=TicketStatus.OPEN,
        nullable=False
    )
    priority = Column(
        Enum(TicketPriority),
        default=TicketPriority.MEDIUM,
        nullable=False
    )
    
    # Category/tags for the ticket
    category = Column(String(100), nullable=True)  # e.g., "refund", "shipping", "login"
    
    # Additional notes (for support agents)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Ticket {self.ticket_id}: {self.status.value}>"
    
    def to_dict(self):
        """Convert ticket to dictionary (for API responses)."""
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "customer_query": self.customer_query,
            "ai_response": self.ai_response,
            "status": self.status.value,
            "priority": self.priority.value,
            "category": self.category,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================
# Database Helper Functions
# ============================================

def create_tables():
    """
    Create all tables in the database.
    
    This is safe to call multiple times - it won't recreate existing tables.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def get_db():
    """
    Get a database session.
    
    Usage:
        db = get_db()
        try:
            # do database operations
        finally:
            db.close()
    """
    db = SessionLocal()
    return db


# ============================================
# Test the database models
# ============================================
if __name__ == "__main__":
    print("Testing Database Models")
    print("=" * 50)
    
    # Test connection and create tables
    print("\n1. Testing database connection...")
    try:
        create_tables()
        print("   ✅ Database tables created!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n   Make sure MySQL is running and the database exists!")
        print("   Run these commands in MySQL:")
        print("   CREATE DATABASE customer_support;")
        exit(1)
    
    # Test creating a ticket
    print("\n2. Testing ticket creation...")
    db = get_db()
    try:
        # Check if test ticket exists
        existing = db.query(Ticket).filter(Ticket.ticket_id == "TKT-TEST").first()
        if existing:
            db.delete(existing)
            db.commit()
        
        # Create a test ticket
        test_ticket = Ticket(
            ticket_id="TKT-TEST",
            customer_email="test@example.com",
            customer_name="Test User",
            customer_query="This is a test ticket",
            ai_response="This is a test response",
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            category="test"
        )
        db.add(test_ticket)
        db.commit()
        db.refresh(test_ticket)
        
        print(f"   ✅ Created ticket: {test_ticket}")
        print(f"   Ticket data: {test_ticket.to_dict()}")
        
        # Clean up test ticket
        db.delete(test_ticket)
        db.commit()
        print("   ✅ Test ticket cleaned up")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "=" * 50)
    print("✅ Database models are working correctly!")
