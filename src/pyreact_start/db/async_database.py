"""
Asynchronous database connection and query execution.

Provides AsyncDatabase and AsyncTypedConnection with query methods.
Requires async SQLAlchemy driver (e.g., aiosqlite, asyncpg).
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from .errors import NotFoundError, TooManyRowsError, ValidationError
from .hooks import Hook, HookChain, QueryContext
from .types import T, TypedQuery


class AsyncTypedConnection:
    """
    Async wrapper around SQLAlchemy AsyncConnection providing type-safe query methods.

    Provides these methods:
    - `one()`: Exactly one row (raises if 0 or >1)
    - `maybe_one()`: Zero or one row (raises if >1)
    - `many()`: One or more rows (raises if 0)
    - `any()`: Zero or more rows (never raises for count)

    All methods support:
    - `params`: Optional dict for bindparam queries
    - `skip_validation`: Bypass Pydantic validation for performance
    """

    __slots__ = ("_conn", "_hooks")

    def __init__(
        self, conn: AsyncConnection, hooks: HookChain | None = None
    ):
        self._conn = conn
        self._hooks = hooks or HookChain()

    async def one(
        self,
        query: TypedQuery[T],
        params: dict[str, Any] | None = None,
        skip_validation: bool = False,
    ) -> T:
        """
        Execute query and return exactly one row.

        Raises:
            NotFoundError: If zero rows returned
            TooManyRowsError: If more than one row returned
            ValidationError: If row fails Pydantic validation
        """
        rows = await self._execute(query, params, skip_validation)
        if len(rows) == 0:
            raise NotFoundError("Expected exactly 1 row, got 0")
        if len(rows) > 1:
            raise TooManyRowsError(f"Expected exactly 1 row, got {len(rows)}")
        return rows[0]

    async def maybe_one(
        self,
        query: TypedQuery[T],
        params: dict[str, Any] | None = None,
        skip_validation: bool = False,
    ) -> T | None:
        """
        Execute query and return zero or one row.

        Raises:
            TooManyRowsError: If more than one row returned
            ValidationError: If row fails Pydantic validation
        """
        rows = await self._execute(query, params, skip_validation)
        if len(rows) > 1:
            raise TooManyRowsError(f"Expected 0 or 1 row, got {len(rows)}")
        return rows[0] if rows else None

    async def many(
        self,
        query: TypedQuery[T],
        params: dict[str, Any] | None = None,
        skip_validation: bool = False,
    ) -> list[T]:
        """
        Execute query and return one or more rows.

        Raises:
            NotFoundError: If zero rows returned
            ValidationError: If any row fails Pydantic validation
        """
        rows = await self._execute(query, params, skip_validation)
        if len(rows) == 0:
            raise NotFoundError("Expected at least 1 row, got 0")
        return rows

    async def any(
        self,
        query: TypedQuery[T],
        params: dict[str, Any] | None = None,
        skip_validation: bool = False,
    ) -> list[T]:
        """
        Execute query and return zero or more rows.

        Never raises for row count. Use this when empty results are valid.

        Raises:
            ValidationError: If any row fails Pydantic validation
        """
        return await self._execute(query, params, skip_validation)

    async def _execute(
        self, query: TypedQuery[T], params: dict[str, Any] | None, skip_validation: bool
    ) -> list[T]:
        """Internal: execute query with hooks and validate results."""
        # Create context for hooks
        ctx = QueryContext(
            statement=query.statement,
            model_name=query.model.__name__,
            params=params,
            skip_validation=skip_validation,
        )

        try:
            # Run before hooks (sync - hooks are sync even in async context)
            self._hooks.run_before(ctx)

            # Execute query
            result = await self._conn.execute(ctx.statement, ctx.params)

            # Convert to list of dicts
            rows: list[dict[str, Any]] = [dict(row._mapping) for row in result]

            # Run after hooks (can transform rows)
            rows = self._hooks.run_after(ctx, rows)

            # Validate with Pydantic
            validated: list[T] = []
            for row_dict in rows:
                if skip_validation:
                    # Performance bypass: construct without validation
                    validated.append(query.model.model_construct(**row_dict))
                else:
                    # Full runtime validation
                    try:
                        validated.append(query.model.model_validate(row_dict))
                    except PydanticValidationError as e:
                        raise ValidationError(
                            f"Row validation failed for {query.model.__name__}: {e}",
                            e.errors(),
                        ) from e

            return validated

        except Exception as e:
            # Run error hooks
            error = self._hooks.run_on_error(ctx, e)
            raise error from None


class AsyncDatabase:
    """
    Asynchronous database connection manager.

    Wraps a SQLAlchemy AsyncEngine and provides async context managers for
    connections and transactions with type-safe query execution.

    Requires an async database driver:
    - SQLite: aiosqlite (url: "sqlite+aiosqlite:///app.db")
    - PostgreSQL: asyncpg (url: "postgresql+asyncpg://...")
    - MySQL: aiomysql (url: "mysql+aiomysql://...")

    Example:
        ```python
        from pyreact_start.db import AsyncDatabase, LoggingHook

        db = AsyncDatabase(
            "sqlite+aiosqlite:///app.db",
            hooks=[LoggingHook()]
        )

        async with db.connection() as conn:
            user = await conn.one(get_user(42))
            # Console: [SQL] User: 1 rows in 0.52ms

        async with db.transaction() as conn:
            await conn.one(create_user("Alice"))
            # Auto-commits on success, rollback on exception
        ```
    """

    def __init__(
        self,
        url: str,
        hooks: list[Hook] | None = None,
        **engine_kwargs: Any,
    ):
        """
        Create an AsyncDatabase instance.

        Args:
            url: SQLAlchemy async database URL (e.g., "sqlite+aiosqlite:///app.db")
            hooks: Optional list of Hook instances
            **engine_kwargs: Additional arguments passed to create_async_engine
        """
        self.engine: AsyncEngine = create_async_engine(url, **engine_kwargs)
        self._hooks = HookChain(hooks)

    def add_hook(self, hook: Hook) -> None:
        """Add an hook to the chain."""
        self._hooks.add(hook)

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[AsyncTypedConnection, None]:
        """
        Get an async connection context manager.

        Connection is automatically closed when context exits.
        Does NOT auto-commit - use transaction() for that.
        """
        async with self.engine.connect() as conn:
            yield AsyncTypedConnection(conn, self._hooks)

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncTypedConnection, None]:
        """
        Get an async transaction context manager.

        - Auto-commits when context exits normally
        - Auto-rolls back when an exception is raised
        """
        async with self.engine.begin() as conn:
            yield AsyncTypedConnection(conn, self._hooks)

    async def dispose(self) -> None:
        """Dispose of the connection pool."""
        await self.engine.dispose()
