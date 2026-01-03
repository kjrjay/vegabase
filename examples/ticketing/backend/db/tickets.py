"""
Ticket CRUD operations.
"""

from datetime import UTC

from sqlalchemy import delete, insert, select, update
from vegabase.db import query

from . import db
from .schema import Ticket, TicketWithAuthor, tickets, users


async def get_all_tickets() -> list[Ticket]:
    """Get all tickets."""
    async with db.connection() as conn:
        return await conn.all(
            query(Ticket, select(tickets).order_by(tickets.c.created_at.desc()))
        )


async def get_tickets_with_author() -> list[TicketWithAuthor]:
    """Get all tickets with author names for public view."""
    async with db.connection() as conn:
        stmt = (
            select(
                tickets.c.id,
                tickets.c.title,
                tickets.c.description,
                tickets.c.status,
                tickets.c.created_at,
                users.c.name.label("author_name"),
            )
            .select_from(tickets.join(users, tickets.c.created_by == users.c.id))
            .order_by(tickets.c.created_at.desc())
        )
        return await conn.all(query(TicketWithAuthor, stmt))


async def get_ticket(ticket_id: int) -> Ticket | None:
    """Get a single ticket by ID."""
    async with db.connection() as conn:
        return await conn.maybe_one(
            query(Ticket, select(tickets).where(tickets.c.id == ticket_id))
        )


async def add_ticket(user_id: int, title: str, description: str) -> int:
    """Add a ticket created by a specific user."""
    from datetime import datetime

    created_at = datetime.now(UTC).isoformat()
    async with db.transaction() as conn:
        result = await conn._conn.execute(
            insert(tickets).values(
                created_by=user_id,
                title=title,
                description=description,
                status="open",
                created_at=created_at,
            )
        )
        return result.lastrowid or 0


async def update_ticket(
    ticket_id: int,
    status: str | None = None,
    title: str | None = None,
    description: str | None = None,
) -> None:
    """Update ticket fields."""
    async with db.transaction() as conn:
        values = {}
        if status is not None:
            values["status"] = status
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if values:
            await conn.execute(
                update(tickets).where(tickets.c.id == ticket_id).values(**values)
            )


async def delete_ticket(ticket_id: int) -> None:
    """Delete a ticket."""
    async with db.transaction() as conn:
        await conn.execute(delete(tickets).where(tickets.c.id == ticket_id))
