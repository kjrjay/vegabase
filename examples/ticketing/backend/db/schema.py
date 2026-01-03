"""
Database schema and models.
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
)

# Database URL (required by vegabase CLI)
DATABASE_URL = "sqlite:///tasks.db"

# Schema definition
metadata = MetaData()

tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("title", String, nullable=False),
    Column("completed", Boolean, nullable=False, default=False),
)

tickets = Table(
    "tickets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("created_by", Integer, nullable=False),
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
    user_id: int
    title: str
    completed: bool


class Ticket(BaseModel):
    id: int
    created_by: int
    title: str
    description: str | None
    status: str
    created_at: str | None


class TicketWithAuthor(BaseModel):
    """Ticket with author name for public view."""

    id: int
    title: str
    description: str | None
    status: str
    created_at: str | None
    author_name: str


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
