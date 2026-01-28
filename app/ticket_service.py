# ============================================
# Ticket Service
# ============================================
# This module handles all ticket-related operations.
#
# Features:
# - Create new support tickets
# - Get ticket by ID
# - Update ticket status
# - List all tickets
# - Auto-generate ticket IDs (TKT-00001, TKT-00002, etc.)

from typing import Dict, List, Optional
from datetime import datetime

from app.models import (
    Ticket,
    TicketStatus,
    TicketPriority,
    get_db,
    create_tables
)


def generate_ticket_id(db) -> str:
    """
    Generate a unique ticket ID.
    
    Format: TKT-XXXXX (e.g., TKT-00001, TKT-00042)
    
    Args:
        db: Database session
    
    Returns:
        New unique ticket ID
    """
    # Get the highest existing ticket number
    last_ticket = db.query(Ticket).order_by(Ticket.id.desc()).first()
    
    if last_ticket:
        # Extract number from last ticket ID and increment
        next_num = last_ticket.id + 1
    else:
        next_num = 1
    
    return f"TKT-{next_num:05d}"  # Format as 5 digits (TKT-00001)


def create_ticket(
    customer_query: str,
    ai_response: str = None,
    customer_email: str = None,
    customer_name: str = None,
    priority: str = "medium",
    category: str = None
) -> Dict:
    """
    Create a new support ticket.
    
    This is called automatically when a complaint is detected,
    or manually when a customer wants to create a ticket.
    
    Args:
        customer_query: The customer's original question/complaint
        ai_response: The chatbot's response (optional)
        customer_email: Customer's email (optional)
        customer_name: Customer's name (optional)
        priority: Priority level (low, medium, high, urgent)
        category: Category of the issue (optional)
    
    Returns:
        Dict with ticket information
    
    Example:
        ticket = create_ticket(
            customer_query="My order never arrived!",
            ai_response="I'm sorry to hear that...",
            customer_email="customer@example.com",
            priority="high"
        )
        print(f"Ticket created: {ticket['ticket_id']}")
    """
    db = get_db()
    
    try:
        # Generate unique ticket ID
        ticket_id = generate_ticket_id(db)
        
        # Map priority string to enum
        priority_map = {
            "low": TicketPriority.LOW,
            "medium": TicketPriority.MEDIUM,
            "high": TicketPriority.HIGH,
            "urgent": TicketPriority.URGENT
        }
        priority_enum = priority_map.get(priority.lower(), TicketPriority.MEDIUM)
        
        # Create the ticket
        ticket = Ticket(
            ticket_id=ticket_id,
            customer_query=customer_query,
            ai_response=ai_response,
            customer_email=customer_email,
            customer_name=customer_name,
            status=TicketStatus.OPEN,
            priority=priority_enum,
            category=category
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        print(f"✅ Ticket created: {ticket_id}")
        
        return {
            "success": True,
            "ticket": ticket.to_dict(),
            "message": f"Ticket {ticket_id} created successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating ticket: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create ticket"
        }
    finally:
        db.close()


def get_ticket(ticket_id: str) -> Optional[Dict]:
    """
    Get a ticket by its ID.
    
    Args:
        ticket_id: The ticket ID (e.g., "TKT-00001")
    
    Returns:
        Ticket data as dict, or None if not found
    
    Example:
        ticket = get_ticket("TKT-00001")
        if ticket:
            print(f"Status: {ticket['status']}")
    """
    db = get_db()
    
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        
        if ticket:
            return ticket.to_dict()
        else:
            return None
            
    finally:
        db.close()


def update_ticket_status(
    ticket_id: str,
    status: str,
    notes: str = None
) -> Dict:
    """
    Update the status of a ticket.
    
    Args:
        ticket_id: The ticket ID to update
        status: New status (open, in_progress, resolved, closed)
        notes: Optional notes about the update
    
    Returns:
        Dict with success status and updated ticket
    """
    db = get_db()
    
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
        
        if not ticket:
            return {
                "success": False,
                "error": "Ticket not found",
                "message": f"No ticket found with ID {ticket_id}"
            }
        
        # Map status string to enum
        status_map = {
            "open": TicketStatus.OPEN,
            "in_progress": TicketStatus.IN_PROGRESS,
            "resolved": TicketStatus.RESOLVED,
            "closed": TicketStatus.CLOSED
        }
        
        status_enum = status_map.get(status.lower())
        if not status_enum:
            return {
                "success": False,
                "error": "Invalid status",
                "message": f"Valid statuses: {list(status_map.keys())}"
            }
        
        # Update the ticket
        ticket.status = status_enum
        if notes:
            ticket.notes = notes
        ticket.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        print(f"✅ Ticket {ticket_id} updated to {status}")
        
        return {
            "success": True,
            "ticket": ticket.to_dict(),
            "message": f"Ticket {ticket_id} updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update ticket"
        }
    finally:
        db.close()


def list_tickets(
    status: str = None,
    limit: int = 50
) -> List[Dict]:
    """
    List all tickets, optionally filtered by status.
    
    Args:
        status: Filter by status (optional)
        limit: Maximum number of tickets to return
    
    Returns:
        List of ticket dictionaries
    """
    db = get_db()
    
    try:
        query = db.query(Ticket)
        
        # Filter by status if provided
        if status:
            status_map = {
                "open": TicketStatus.OPEN,
                "in_progress": TicketStatus.IN_PROGRESS,
                "resolved": TicketStatus.RESOLVED,
                "closed": TicketStatus.CLOSED
            }
            status_enum = status_map.get(status.lower())
            if status_enum:
                query = query.filter(Ticket.status == status_enum)
        
        # Order by most recent first
        query = query.order_by(Ticket.created_at.desc())
        
        # Apply limit
        tickets = query.limit(limit).all()
        
        return [ticket.to_dict() for ticket in tickets]
        
    finally:
        db.close()


def get_ticket_stats() -> Dict:
    """
    Get ticket statistics.
    
    Returns:
        Dict with counts by status
    """
    db = get_db()
    
    try:
        stats = {
            "total": db.query(Ticket).count(),
            "open": db.query(Ticket).filter(Ticket.status == TicketStatus.OPEN).count(),
            "in_progress": db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).count(),
            "resolved": db.query(Ticket).filter(Ticket.status == TicketStatus.RESOLVED).count(),
            "closed": db.query(Ticket).filter(Ticket.status == TicketStatus.CLOSED).count(),
        }
        return stats
        
    finally:
        db.close()


# ============================================
# Test the ticket service
# ============================================
if __name__ == "__main__":
    print("Testing Ticket Service")
    print("=" * 50)
    
    # Ensure tables exist
    print("\n1. Ensuring database tables exist...")
    try:
        create_tables()
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        print("\n   Make sure MySQL is running and database exists!")
        print("   Run in MySQL: CREATE DATABASE customer_support;")
        exit(1)
    
    # Test creating a ticket
    print("\n2. Creating a test ticket...")
    result = create_ticket(
        customer_query="My order #12345 never arrived! I've been waiting for 2 weeks!",
        ai_response="I'm sorry to hear about your order delay. I've found information about our shipping policy...",
        customer_email="angry.customer@example.com",
        customer_name="John Doe",
        priority="high",
        category="shipping"
    )
    
    if result["success"]:
        ticket_id = result["ticket"]["ticket_id"]
        print(f"   ✅ Created: {ticket_id}")
        print(f"   Details: {result['ticket']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
        exit(1)
    
    # Test getting a ticket
    print(f"\n3. Retrieving ticket {ticket_id}...")
    ticket = get_ticket(ticket_id)
    if ticket:
        print(f"   ✅ Found ticket: {ticket['ticket_id']}")
        print(f"   Status: {ticket['status']}")
        print(f"   Priority: {ticket['priority']}")
    else:
        print("   ❌ Ticket not found")
    
    # Test updating ticket status
    print(f"\n4. Updating ticket to 'in_progress'...")
    update_result = update_ticket_status(
        ticket_id,
        status="in_progress",
        notes="Agent assigned: Sarah"
    )
    if update_result["success"]:
        print(f"   ✅ Updated: {update_result['ticket']['status']}")
    else:
        print(f"   ❌ Failed: {update_result['error']}")
    
    # Test listing tickets
    print("\n5. Listing all tickets...")
    tickets = list_tickets()
    print(f"   Found {len(tickets)} ticket(s)")
    for t in tickets[:3]:  # Show first 3
        print(f"   - {t['ticket_id']}: {t['status']} ({t['priority']})")
    
    # Test ticket stats
    print("\n6. Getting ticket statistics...")
    stats = get_ticket_stats()
    print(f"   Total: {stats['total']}")
    print(f"   Open: {stats['open']}")
    print(f"   In Progress: {stats['in_progress']}")
    print(f"   Resolved: {stats['resolved']}")
    print(f"   Closed: {stats['closed']}")
    
    print("\n" + "=" * 50)
    print("✅ Ticket service is working correctly!")
