"""
Tests for async Victor library.
"""

import pytest
import pytest_asyncio
from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table, select, text

from pyreact_start.db import (
    AsyncDatabase,
    NotFoundError,
    TooManyRowsError,
    TypedQuery,
    query,
)

# Test fixtures
metadata = MetaData()
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("email", String),
)


class User(BaseModel):
    id: int
    name: str
    email: str


@pytest_asyncio.fixture
async def async_db():
    """Create an in-memory async SQLite database with test data."""
    database = AsyncDatabase("sqlite+aiosqlite:///:memory:")

    # Create table
    async with database.engine.begin() as conn:
        await conn.execute(
            text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        )
        await conn.execute(
            text(
                "INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"
            )
        )
        await conn.execute(
            text(
                "INSERT INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')"
            )
        )

    yield database
    await database.dispose()


@pytest.mark.asyncio
class TestAsyncOne:
    """Test async conn.one() method."""

    async def test_one_returns_single_row(self, async_db):
        def get_user(user_id: int) -> TypedQuery[User]:
            return query(User, select(users).where(users.c.id == user_id))

        async with async_db.connection() as conn:
            user = await conn.one(get_user(1))
            assert isinstance(user, User)
            assert user.id == 1
            assert user.name == "Alice"

    async def test_one_raises_not_found_on_zero_rows(self, async_db):
        q = query(User, select(users).where(users.c.id == 999))

        async with async_db.connection() as conn:
            with pytest.raises(NotFoundError):
                await conn.one(q)

    async def test_one_raises_too_many_on_multiple_rows(self, async_db):
        q = query(User, select(users))

        async with async_db.connection() as conn:
            with pytest.raises(TooManyRowsError):
                await conn.one(q)


@pytest.mark.asyncio
class TestAsyncAny:
    """Test async conn.all() method."""

    async def test_any_returns_multiple_rows(self, async_db):
        q = query(User, select(users))

        async with async_db.connection() as conn:
            users_list = await conn.all(q)
            assert len(users_list) == 2
            assert all(isinstance(u, User) for u in users_list)

    async def test_any_returns_empty_list_on_zero_rows(self, async_db):
        q = query(User, select(users).where(users.c.id == 999))

        async with async_db.connection() as conn:
            users_list = await conn.all(q)
            assert users_list == []


@pytest.mark.asyncio
class TestAsyncTransaction:
    """Test async transaction context manager."""

    async def test_transaction_commits_on_success(self, async_db):
        async with async_db.transaction() as conn:
            await conn._conn.execute(
                text(
                    "INSERT INTO users (id, name, email) VALUES (3, 'Charlie', 'charlie@example.com')"
                )
            )

        # Verify data was committed
        q = query(User, select(users).where(users.c.id == 3))
        async with async_db.connection() as conn:
            user = await conn.one(q)
            assert user.name == "Charlie"
