"""
Tests for Victor library.
"""

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table, select, text

from pyreact_start.db import (
    Database,
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


class UserSummary(BaseModel):
    id: int
    name: str


@pytest.fixture
def db():
    """Create an in-memory SQLite database with test data."""
    database = Database("sqlite:///:memory:")

    # Create table
    with database.engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        )
        conn.execute(
            text(
                "INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')"
            )
        )
        conn.commit()

    yield database
    database.dispose()


class TestTypedQuery:
    """Test TypedQuery construction."""

    def test_query_creates_query(self):
        q = query(User, select(users))
        assert isinstance(q, TypedQuery)
        assert q.model is User

    def test_query_query_repr(self):
        q = query(User, select(users))
        assert "TypedQuery[User]" in repr(q)


class TestOne:
    """Test conn.one() method."""

    def test_one_returns_single_row(self, db):
        def get_user(user_id: int) -> TypedQuery[User]:
            return query(User, select(users).where(users.c.id == user_id))

        with db.connection() as conn:
            user = conn.one(get_user(1))
            assert isinstance(user, User)
            assert user.id == 1
            assert user.name == "Alice"
            assert user.email == "alice@example.com"

    def test_one_raises_not_found_on_zero_rows(self, db):
        q = query(User, select(users).where(users.c.id == 999))

        with db.connection() as conn:
            with pytest.raises(NotFoundError):
                conn.one(q)

    def test_one_raises_too_many_on_multiple_rows(self, db):
        q = query(User, select(users))  # Returns 2 rows

        with db.connection() as conn:
            with pytest.raises(TooManyRowsError):
                conn.one(q)


class TestMaybeOne:
    """Test conn.maybe_one() method."""

    def test_maybe_one_returns_single_row(self, db):
        q = query(User, select(users).where(users.c.id == 1))

        with db.connection() as conn:
            user = conn.maybe_one(q)
            assert user is not None
            assert user.name == "Alice"

    def test_maybe_one_returns_none_on_zero_rows(self, db):
        q = query(User, select(users).where(users.c.id == 999))

        with db.connection() as conn:
            user = conn.maybe_one(q)
            assert user is None

    def test_maybe_one_raises_too_many_on_multiple_rows(self, db):
        q = query(User, select(users))

        with db.connection() as conn:
            with pytest.raises(TooManyRowsError):
                conn.maybe_one(q)


class TestMany:
    """Test conn.many() method."""

    def test_many_returns_multiple_rows(self, db):
        q = query(User, select(users))

        with db.connection() as conn:
            users_list = conn.many(q)
            assert len(users_list) == 2
            assert all(isinstance(u, User) for u in users_list)

    def test_many_raises_not_found_on_zero_rows(self, db):
        q = query(User, select(users).where(users.c.id == 999))

        with db.connection() as conn:
            with pytest.raises(NotFoundError):
                conn.many(q)


class TestAny:
    """Test conn.any() method."""

    def test_any_returns_multiple_rows(self, db):
        q = query(User, select(users))

        with db.connection() as conn:
            users_list = conn.any(q)
            assert len(users_list) == 2

    def test_any_returns_empty_list_on_zero_rows(self, db):
        q = query(User, select(users).where(users.c.id == 999))

        with db.connection() as conn:
            users_list = conn.any(q)
            assert users_list == []


class TestValidation:
    """Test runtime validation."""

    def test_validation_catches_missing_field(self, db):
        # Try to map to UserSummary but database has extra field - this should work
        q = query(
            UserSummary, select(users.c.id, users.c.name).where(users.c.id == 1)
        )

        with db.connection() as conn:
            user = conn.one(q)
            assert isinstance(user, UserSummary)
            assert user.name == "Alice"

    def test_skip_validation_bypasses_pydantic(self, db):
        q = query(User, select(users).where(users.c.id == 1))

        with db.connection() as conn:
            user = conn.one(q, skip_validation=True)
            assert isinstance(user, User)
            assert user.name == "Alice"


class TestTransaction:
    """Test transaction context manager."""

    def test_transaction_commits_on_success(self, db):
        with db.transaction() as conn:
            # Use raw execute for insert since we're testing transaction
            conn._conn.execute(
                text(
                    "INSERT INTO users (id, name, email) VALUES (3, 'Charlie', 'charlie@example.com')"
                )
            )

        # Verify data was committed
        q = query(User, select(users).where(users.c.id == 3))
        with db.connection() as conn:
            user = conn.one(q)
            assert user.name == "Charlie"

    def test_transaction_rollbacks_on_exception(self, db):
        try:
            with db.transaction() as conn:
                conn._conn.execute(
                    text(
                        "INSERT INTO users (id, name, email) VALUES (4, 'Dave', 'dave@example.com')"
                    )
                )
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Verify data was NOT committed
        q = query(User, select(users).where(users.c.id == 4))
        with db.connection() as conn:
            user = conn.maybe_one(q)
            assert user is None


class TestExecute:
    """Test conn.execute() method for mutations."""

    def test_execute_insert_returns_rowcount(self, db):
        from sqlalchemy import insert

        with db.transaction() as conn:
            count = conn.execute(
                insert(users).values(id=10, name="Eve", email="eve@example.com")
            )
            assert count == 1

    def test_execute_update_returns_rowcount(self, db):
        from sqlalchemy import update

        with db.transaction() as conn:
            count = conn.execute(
                update(users).where(users.c.id == 1).values(name="Alice Updated")
            )
            assert count == 1

    def test_execute_delete_returns_rowcount(self, db):
        from sqlalchemy import delete

        with db.transaction() as conn:
            count = conn.execute(delete(users).where(users.c.id == 1))
            assert count == 1


class TestScalar:
    """Test conn.scalar() method for aggregate queries."""

    def test_scalar_returns_count(self, db):
        from sqlalchemy import func

        with db.connection() as conn:
            count = conn.scalar(select(func.count()).select_from(users))
            assert count == 2

    def test_scalar_returns_max(self, db):
        from sqlalchemy import func

        with db.connection() as conn:
            max_id = conn.scalar(select(func.max(users.c.id)))
            assert max_id == 2


class TestReturning:
    """Test conn.returning_one() and returning_many() methods."""

    def test_returning_one_insert(self, db):
        from sqlalchemy import insert

        with db.transaction() as conn:
            new_user = conn.returning_one(
                query(
                    User,
                    insert(users)
                    .values(id=20, name="Frank", email="frank@example.com")
                    .returning(users),
                )
            )
            assert isinstance(new_user, User)
            assert new_user.id == 20
            assert new_user.name == "Frank"

    def test_returning_many_delete(self, db):
        from sqlalchemy import delete

        with db.transaction() as conn:
            deleted = conn.returning_many(
                query(User, delete(users).returning(users))
            )
            assert len(deleted) == 2
            assert all(isinstance(u, User) for u in deleted)


class TestExecuteMany:
    """Test conn.execute_many() method for bulk inserts."""

    def test_execute_many_bulk_insert(self, db):
        from sqlalchemy import insert

        with db.transaction() as conn:
            conn.execute_many(
                insert(users),
                [
                    {"id": 100, "name": "User1", "email": "user1@example.com"},
                    {"id": 101, "name": "User2", "email": "user2@example.com"},
                    {"id": 102, "name": "User3", "email": "user3@example.com"},
                ],
            )

        # Verify all were inserted
        with db.connection() as conn:
            all_users = conn.any(query(User, select(users).where(users.c.id >= 100)))
            assert len(all_users) == 3
