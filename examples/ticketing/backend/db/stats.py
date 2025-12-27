"""
Dashboard statistics.
"""

from sqlalchemy import func, select

from . import db
from .schema import tasks, tickets


async def get_dashboard_stats(user_id: int | None = None) -> dict:
    """Get dashboard statistics."""
    async with db.connection() as conn:
        # Task stats (user-specific, requires login)
        task_stats = {"total": 0, "completed": 0, "pending": 0}
        if user_id:
            task_count = await conn._conn.scalar(
                select(func.count()).select_from(tasks).where(tasks.c.user_id == user_id)
            ) or 0
            completed_count = await conn._conn.scalar(
                select(func.count()).select_from(tasks).where(
                    (tasks.c.user_id == user_id) & (tasks.c.completed == True)  # noqa: E712
                )
            ) or 0
            task_stats = {
                "total": task_count,
                "completed": completed_count,
                "pending": task_count - completed_count,
            }

        # Ticket stats (global)
        total_tickets = await conn._conn.scalar(
            select(func.count()).select_from(tickets)
        ) or 0
        open_tickets = await conn._conn.scalar(
            select(func.count()).select_from(tickets).where(tickets.c.status == "open")
        ) or 0
        closed_tickets = await conn._conn.scalar(
            select(func.count()).select_from(tickets).where(tickets.c.status == "closed")
        ) or 0

        ticket_stats = {
            "total": total_tickets,
            "open": open_tickets,
            "closed": closed_tickets,
        }

        return {
            "tasks": task_stats,
            "tickets": ticket_stats,
        }


async def get_ticket_history(period: str = "weekly") -> list[dict]:
    """Get cumulative ticket counts over time for charting.
    
    Args:
        period: 'weekly' or 'monthly'
    
    Returns:
        List of {date, total, open, closed} dicts with cumulative counts
    """
    from datetime import datetime, timedelta

    async with db.connection() as conn:
        # Get all tickets with their status
        result = await conn._conn.execute(
            select(tickets.c.created_at, tickets.c.status)
        )
        rows = result.fetchall()

    # Group new tickets by period
    new_per_period: dict[str, dict[str, int]] = {}
    
    for row in rows:
        if not row.created_at:
            continue
        
        try:
            dt = datetime.fromisoformat(row.created_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue
        
        if period == "monthly":
            key = dt.strftime("%Y-%m")
        else:  # weekly
            # Get start of week (Monday)
            week_start = dt - timedelta(days=dt.weekday())
            key = week_start.strftime("%Y-%m-%d")
        
        if key not in new_per_period:
            new_per_period[key] = {"total": 0, "open": 0, "closed": 0}
        
        new_per_period[key]["total"] += 1
        if row.status == "open":
            new_per_period[key]["open"] += 1
        elif row.status == "closed":
            new_per_period[key]["closed"] += 1

    # Convert to cumulative counts
    sorted_dates = sorted(new_per_period.keys())
    cumulative: list[dict] = []
    running_total = 0
    running_open = 0
    running_closed = 0
    
    for d in sorted_dates:
        running_total += new_per_period[d]["total"]
        running_open += new_per_period[d]["open"]
        running_closed += new_per_period[d]["closed"]
        cumulative.append({
            "date": d,
            "total": running_total,
            "open": running_open,
            "closed": running_closed,
        })
    
    return cumulative
