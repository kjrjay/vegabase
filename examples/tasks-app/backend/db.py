"""
Database module using pyreact_start.db for type-safe queries.
"""

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    delete,
    insert,
    select,
    update,
)

from pyreact_start.db import AsyncDatabase, query

# Database setup
DB_URL = "sqlite+aiosqlite:///tasks.db"
db = AsyncDatabase(DB_URL)

# Schema definition
metadata = MetaData()

tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("completed", Boolean, nullable=False, default=False),
)

tickets = Table(
    "tickets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", Text),
    Column("status", String, nullable=False, default="open"),
    Column("created_at", String),  # SQLite doesn't have native timestamp
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("name", String, nullable=False),
    Column("avatar_url", String),
    Column("password_hash", String, nullable=False),
)


# Pydantic models
class Task(BaseModel):
    id: int
    title: str
    completed: bool


class Ticket(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    created_at: str | None


class User(BaseModel):
    id: int
    username: str
    name: str
    avatar_url: str | None
    password_hash: str


class UserPublic(BaseModel):
    """User without password hash for sending to client."""

    id: int
    username: str
    name: str
    avatar_url: str | None


# Initialize database
async def init_db():
    """Create all tables if they don't exist."""
    async with db.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    # Create demo user if not exists
    existing = await get_user_by_username("demo")
    if not existing:
        await create_user("demo", "Demo User", "password")
        print("✅ Created demo user (demo/password)")


# Tasks CRUD
async def get_all_tasks() -> list[Task]:
    async with db.connection() as conn:
        return await conn.all(query(Task, select(tasks)))


async def add_task(title: str) -> int:
    async with db.transaction() as conn:
        result = await conn._conn.execute(insert(tasks).values(title=title, completed=False))
        return result.lastrowid or 0


async def update_task(task_id: int, completed: bool) -> None:
    async with db.transaction() as conn:
        await conn.execute(update(tasks).where(tasks.c.id == task_id).values(completed=completed))


async def delete_task(task_id: int) -> None:
    async with db.transaction() as conn:
        await conn.execute(delete(tasks).where(tasks.c.id == task_id))


# Tickets CRUD
async def get_all_tickets() -> list[Ticket]:
    async with db.connection() as conn:
        return await conn.all(
            query(Ticket, select(tickets).order_by(tickets.c.created_at.desc()))
        )


async def get_ticket(ticket_id: int) -> Ticket | None:
    async with db.connection() as conn:
        return await conn.maybe_one(
            query(Ticket, select(tickets).where(tickets.c.id == ticket_id))
        )


async def add_ticket(title: str, description: str) -> int:
    async with db.transaction() as conn:
        result = await conn._conn.execute(
            insert(tickets).values(title=title, description=description, status="open")
        )
        return result.lastrowid or 0


async def update_ticket(
    ticket_id: int,
    status: str | None = None,
    title: str | None = None,
    description: str | None = None,
) -> None:
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
    async with db.transaction() as conn:
        await conn.execute(delete(tickets).where(tickets.c.id == ticket_id))


# Users/Auth
async def get_user_by_username(username: str) -> User | None:
    async with db.connection() as conn:
        return await conn.maybe_one(
            query(User, select(users).where(users.c.username == username))
        )


async def get_user_by_id(user_id: int) -> User | None:
    async with db.connection() as conn:
        return await conn.maybe_one(
            query(User, select(users).where(users.c.id == user_id))
        )


async def create_user(
    username: str, name: str, password: str, avatar_url: str | None = None
) -> int | None:
    import hashlib

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        async with db.transaction() as conn:
            result = await conn._conn.execute(
                insert(users).values(
                    username=username,
                    name=name,
                    password_hash=password_hash,
                    avatar_url=avatar_url,
                )
            )
            return result.lastrowid
    except Exception:
        return None


async def verify_password(username: str, password: str) -> User | None:
    import hashlib

    user = await get_user_by_username(username)
    if not user:
        return None
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.password_hash == password_hash:
        return user
    return None


def user_to_public(user: User) -> dict:
    """Convert User to public dict (no password hash)."""
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "avatar_url": user.avatar_url,
    }
