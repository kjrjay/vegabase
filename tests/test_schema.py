"""
Tests for schema management (plan/apply).
"""

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table

from pyreact_start.db import Database, SchemaChange, apply, create_all, plan, query
from pyreact_start.db.schema import ChangeType


@pytest.fixture
def empty_db():
    """Create an empty in-memory SQLite database."""
    database = Database("sqlite:///:memory:")
    yield database
    database.dispose()


@pytest.fixture
def metadata():
    """Create test metadata with a users table."""
    meta = MetaData()
    Table(
        "users",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", String(100)),
        Column("email", String(255)),
    )
    return meta


class TestPlan:
    """Test plan() function."""

    def test_plan_detects_new_table(self, empty_db, metadata):
        changes = plan(empty_db.engine, metadata)

        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.CREATE_TABLE
        assert changes[0].table_name == "users"

    def test_plan_detects_new_column(self, empty_db):
        # Create table with only id and name
        initial_meta = MetaData()
        Table(
            "users",
            initial_meta,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
        )
        create_all(empty_db.engine, initial_meta)

        # Now plan with additional email column
        updated_meta = MetaData()
        Table(
            "users",
            updated_meta,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
            Column("email", String(255)),
        )

        changes = plan(empty_db.engine, updated_meta)

        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.ADD_COLUMN
        assert changes[0].table_name == "users"
        assert changes[0].detail == "email"

    def test_plan_returns_empty_when_in_sync(self, empty_db, metadata):
        # Create the table first
        create_all(empty_db.engine, metadata)

        # Plan should show no changes
        changes = plan(empty_db.engine, metadata)

        assert len(changes) == 0


class TestApply:
    """Test apply() function."""

    def test_apply_creates_table(self, empty_db, metadata):
        applied = apply(empty_db.engine, metadata)

        # Verify table was created by querying it
        from sqlalchemy import inspect

        inspector = inspect(empty_db.engine)
        tables = inspector.get_table_names()

        assert "users" in tables
        assert len(applied) >= 1

    def test_apply_adds_column(self, empty_db):
        # Create table with only id and name
        initial_meta = MetaData()
        users_initial = Table(
            "users",
            initial_meta,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
        )
        create_all(empty_db.engine, initial_meta)

        # Apply with additional email column
        updated_meta = MetaData()
        Table(
            "users",
            updated_meta,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
            Column("email", String(255)),
        )

        applied = apply(empty_db.engine, updated_meta)

        # Verify column was added
        from sqlalchemy import inspect

        inspector = inspect(empty_db.engine)
        columns = {col["name"] for col in inspector.get_columns("users")}

        assert "email" in columns
        assert len(applied) == 1
        assert applied[0].detail == "email"


class TestCreateAll:
    """Test create_all() function."""

    def test_create_all_creates_tables(self, empty_db, metadata):
        create_all(empty_db.engine, metadata)

        from sqlalchemy import inspect

        inspector = inspect(empty_db.engine)
        tables = inspector.get_table_names()

        assert "users" in tables


class TestSchemaChange:
    """Test SchemaChange dataclass."""

    def test_str_representation(self):
        change = SchemaChange(
            change_type=ChangeType.ADD_COLUMN,
            table_name="users",
            detail="email",
        )
        assert str(change) == "add_column: users.email"

    def test_str_without_detail(self):
        change = SchemaChange(
            change_type=ChangeType.CREATE_TABLE,
            table_name="users",
        )
        assert str(change) == "create_table: users"
