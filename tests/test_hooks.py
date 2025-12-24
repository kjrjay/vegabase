"""
Tests for Victor hooks.
"""

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table, select, text

from pyreact_start.db import (
    CamelCaseHook,
    Database,
    Hook,
    LoggingHook,
    query,
)

# Test fixtures
metadata = MetaData()
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_name", String),  # snake_case for camelCase test
    Column("email_address", String),
)


class User(BaseModel):
    id: int
    user_name: str
    email_address: str


class UserCamel(BaseModel):
    """Model with camelCase fields for CamelCaseHook test."""

    id: int
    userName: str
    emailAddress: str


@pytest.fixture
def db():
    """Create an in-memory SQLite database with test data."""
    database = Database("sqlite:///:memory:")

    with database.engine.connect() as conn:
        conn.execute(
            text(
                "CREATE TABLE users (id INTEGER PRIMARY KEY, user_name TEXT, email_address TEXT)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO users (id, user_name, email_address) VALUES (1, 'alice', 'alice@example.com')"
            )
        )
        conn.commit()

    yield database
    database.dispose()


class TestHookHooks:
    """Test that hook hooks are called."""

    def test_before_and_after_execute_called(self, db):
        calls = []

        class TrackingHook(Hook):
            def before_execute(self, ctx):
                calls.append(("before", ctx.model_name))

            def after_execute(self, ctx, rows):
                calls.append(("after", len(rows)))
                return rows

        db.add_hook(TrackingHook())

        q = query(User, select(users))
        with db.connection() as conn:
            conn.any(q)

        assert calls == [("before", "User"), ("after", 1)]

    def test_on_error_called(self, db):
        calls = []

        class ErrorHook(Hook):
            def on_error(self, ctx, error):
                calls.append(("error", type(error).__name__))
                return error

        db.add_hook(ErrorHook())

        # Query a non-existent table to trigger error
        bad_table = Table("nonexistent", metadata, Column("id", Integer))
        q = query(User, select(bad_table))

        with db.connection() as conn:
            with pytest.raises(Exception):  # noqa: B017
                conn.any(q)

        assert len(calls) == 1
        assert calls[0][0] == "error"


class TestLoggingHook:
    """Test LoggingHook."""

    def test_logs_query_execution(self, db):
        logs = []
        hook = LoggingHook(prefix="[TEST]", log_fn=logs.append)
        db.add_hook(hook)

        q = query(User, select(users))
        with db.connection() as conn:
            conn.any(q)

        assert len(logs) == 1
        assert "[TEST]" in logs[0]
        assert "User" in logs[0]
        assert "1 rows" in logs[0]


class TestCamelCaseHook:
    """Test CamelCaseHook."""

    def test_transforms_field_names(self):
        # Create fresh DB with CamelCaseHook
        db = Database("sqlite:///:memory:", hooks=[CamelCaseHook()])

        with db.engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE TABLE users (id INTEGER PRIMARY KEY, user_name TEXT, email_address TEXT)"
                )
            )
            conn.execute(
                text("INSERT INTO users VALUES (1, 'alice', 'alice@example.com')")
            )
            conn.commit()

        q = query(UserCamel, select(users))

        with db.connection() as conn:
            user = conn.one(q)
            assert user.userName == "alice"
            assert user.emailAddress == "alice@example.com"

        db.dispose()


class TestHookChaining:
    """Test that multiple hooks work together."""

    def test_hooks_run_in_order(self, db):
        order = []

        class FirstHook(Hook):
            def before_execute(self, ctx):
                order.append("first_before")

            def after_execute(self, ctx, rows):
                order.append("first_after")
                return rows

        class SecondHook(Hook):
            def before_execute(self, ctx):
                order.append("second_before")

            def after_execute(self, ctx, rows):
                order.append("second_after")
                return rows

        db.add_hook(FirstHook())
        db.add_hook(SecondHook())

        q = query(User, select(users))
        with db.connection() as conn:
            conn.any(q)

        assert order == ["first_before", "second_before", "first_after", "second_after"]
