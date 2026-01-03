"""
Database module - exports all db functionality.
"""
# ruff: noqa: E402

from vegabase.db import AsyncDatabase

from .schema import (
    DATABASE_URL,
    Task,
    Ticket,
    TicketWithAuthor,
    User,
    UserPublic,
    metadata,
)

# Database instance (async version needs +aiosqlite driver)
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
db = AsyncDatabase(ASYNC_DATABASE_URL)

# Re-export CRUD functions
from datetime import UTC

from .stats import get_dashboard_stats, get_ticket_history
from .tasks import add_task, delete_task, get_tasks_for_user, update_task
from .tickets import (
    add_ticket,
    delete_ticket,
    get_all_tickets,
    get_ticket,
    get_tickets_with_author,
    update_ticket,
)
from .users import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    user_to_public,
    verify_password,
)


async def init_db() -> None:
    import os

    # Seed demo data unless SKIP_SEED is set
    if not os.environ.get("SKIP_SEED"):
        existing = await get_user_by_username("demo")
        if existing:
            return
        await create_user("demo", "Demo User", "password")
        print("✅ Created demo user (demo/password)")
        await _seed_demo_data()
    else:
        print("ℹ️  Skipping demo data (SKIP_SEED=1)")


async def _seed_demo_data() -> None:
    """Seed database with sample data for demo purposes."""
    from datetime import datetime, timedelta

    from sqlalchemy import insert as sql_insert

    from .schema import tasks, tickets

    demo_user = await get_user_by_username("demo")
    if not demo_user:
        return

    user_id = demo_user.id
    now = datetime.now(UTC)

    # Sample tickets spread over past 8 weeks
    ticket_data = [
        # Week 1 (8 weeks ago)
        {"title": "Setup CI/CD pipeline", "status": "closed", "days_ago": 56},
        {"title": "Configure monitoring", "status": "closed", "days_ago": 54},
        # Week 2
        {"title": "Database optimization", "status": "closed", "days_ago": 49},
        {"title": "Fix login issues", "status": "closed", "days_ago": 47},
        {"title": "Update dependencies", "status": "closed", "days_ago": 45},
        # Week 3
        {"title": "Add user dashboard", "status": "closed", "days_ago": 42},
        {"title": "Performance review", "status": "closed", "days_ago": 40},
        # Week 4
        {"title": "Mobile responsive design", "status": "closed", "days_ago": 35},
        {"title": "API rate limiting", "status": "closed", "days_ago": 33},
        {"title": "Security audit", "status": "closed", "days_ago": 30},
        # Week 5
        {"title": "Add search feature", "status": "closed", "days_ago": 28},
        {"title": "Email notifications", "status": "open", "days_ago": 25},
        # Week 6
        {"title": "Export to PDF", "status": "open", "days_ago": 21},
        {"title": "Dark mode support", "status": "open", "days_ago": 19},
        {"title": "Bulk operations", "status": "closed", "days_ago": 17},
        # Week 7
        {"title": "Webhook integrations", "status": "open", "days_ago": 14},
        {"title": "Improve onboarding", "status": "open", "days_ago": 12},
        {"title": "Fix timezone issues", "status": "closed", "days_ago": 10},
        # Week 8 (this week)
        {"title": "Add chart analytics", "status": "open", "days_ago": 7},
        {"title": "User feedback form", "status": "open", "days_ago": 5},
        {"title": "Performance optimization", "status": "open", "days_ago": 3},
        {"title": "Documentation update", "status": "open", "days_ago": 1},
    ]

    async with db.transaction() as conn:
        for t in ticket_data:
            created_at = (now - timedelta(days=t["days_ago"])).isoformat()
            await conn._conn.execute(
                sql_insert(tickets).values(
                    created_by=user_id,
                    title=t["title"],
                    description=f"Sample ticket: {t['title']}",
                    status=t["status"],
                    created_at=created_at,
                )
            )

    # Sample tasks for the demo user
    task_data = [
        {"title": "Review pull requests", "completed": True},
        {"title": "Update documentation", "completed": True},
        {"title": "Fix bug in login flow", "completed": True},
        {"title": "Write unit tests", "completed": False},
        {"title": "Deploy to staging", "completed": False},
        {"title": "Code review meeting", "completed": True},
        {"title": "Optimize database queries", "completed": False},
        {"title": "Setup monitoring alerts", "completed": True},
    ]

    async with db.transaction() as conn:
        for t in task_data:
            await conn._conn.execute(
                sql_insert(tasks).values(
                    user_id=user_id,
                    title=t["title"],
                    completed=t["completed"],
                )
            )

    print("✅ Seeded demo data (22 tickets, 8 tasks)")


__all__ = [
    # Database
    "db",
    "init_db",
    "metadata",
    # Models
    "Task",
    "Ticket",
    "TicketWithAuthor",
    "User",
    "UserPublic",
    # Tasks
    "get_tasks_for_user",
    "add_task",
    "update_task",
    "delete_task",
    # Tickets
    "get_all_tickets",
    "get_tickets_with_author",
    "get_ticket",
    "add_ticket",
    "update_ticket",
    "delete_ticket",
    "get_user_by_username",
    "get_user_by_id",
    "create_user",
    "verify_password",
    "user_to_public",
    # Stats
    "get_dashboard_stats",
    "get_ticket_history",
]
