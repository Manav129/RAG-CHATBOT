#!/usr/bin/env python3
"""
Quick script to check tickets in the database.
"""

from app.ticket_service import list_tickets, get_ticket_stats

print("=" * 60)
print("TICKET DATABASE STATUS")
print("=" * 60)

# Get stats
stats = get_ticket_stats()
print(f"\nTotal Tickets: {stats['total']}")
print(f"Open: {stats.get('open', 0)}")
print(f"In Progress: {stats.get('in_progress', 0)}")
print(f"Resolved: {stats.get('resolved', 0)}")
print(f"Closed: {stats.get('closed', 0)}")

# Get all tickets
tickets = list_tickets()

print(f"\n\n{'='*60}")
print("ALL TICKETS")
print(f"{'='*60}\n")

for ticket in tickets:
    print(f"Ticket ID: {ticket['ticket_id']}")
    print(f"  Status: {ticket['status'].upper()}")
    print(f"  Priority: {ticket['priority'].upper()}")
    print(f"  Category: {ticket.get('category', 'N/A')}")
    print(f"  Query: {ticket['customer_query'][:80]}...")
    print(f"  Created: {ticket['created_at']}")
    print()

print(f"{'='*60}")
