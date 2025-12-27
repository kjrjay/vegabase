"""
Task CRUD operations.
"""

from sqlalchemy import delete, insert, select, update

from vegabase.db import query

from . import db
from .schema import Task, tasks


async def get_tasks_for_user(user_id: int) -> list[Task]:
    """Get all tasks for a specific user."""
    async with db.connection() as conn:
        return await conn.all(
            query(Task, select(tasks).where(tasks.c.user_id == user_id))
        )


async def add_task(user_id: int, title: str) -> int:
    """Add a task for a specific user."""
    async with db.transaction() as conn:
        result = await conn._conn.execute(
            insert(tasks).values(user_id=user_id, title=title, completed=False)
        )
        return result.lastrowid or 0


async def update_task(task_id: int, completed: bool) -> None:
    """Update task completion status."""
    async with db.transaction() as conn:
        await conn.execute(
            update(tasks).where(tasks.c.id == task_id).values(completed=completed)
        )


async def delete_task(task_id: int) -> None:
    """Delete a task."""
    async with db.transaction() as conn:
        await conn.execute(delete(tasks).where(tasks.c.id == task_id))
