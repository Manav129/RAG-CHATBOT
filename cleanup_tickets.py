#!/usr/bin/env python3
"""
Clean up incorrectly created tickets for non-complaint queries.
"""

from app.models import get_db, Ticket

db = get_db()

try:
    # Find tickets that shouldn't have been created (just "refund" queries without complaint words)
    refund_only_queries = [
        "refund policy",
        "refund",
        "what is refund policy",
        "What is the refund policy?"
    ]
    
    deleted_count = 0
    for query in refund_only_queries:
        tickets = db.query(Ticket).filter(Ticket.customer_query.like(f"%{query}%")).all()
        for ticket in tickets:
            # Only delete if it's a simple question (no complaint words)
            if not any(word in ticket.customer_query.lower() for word in ['frustrated', 'angry', 'terrible', 'never', 'still waiting']):
                print(f"Deleting {ticket.ticket_id}: {ticket.customer_query}")
                db.delete(ticket)
                deleted_count += 1
    
    db.commit()
    print(f"\n✅ Deleted {deleted_count} incorrect tickets")
    
    # Show remaining tickets
    remaining = db.query(Ticket).count()
    print(f"Remaining tickets: {remaining}")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()
