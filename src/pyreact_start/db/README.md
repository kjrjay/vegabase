# pyreact_start.db

**Strict SQL** — A type-safe database client for Python

A DB adapter which uses SQLAlchemy Core for query composition and Pydantic for runtime validation. 

- **Static type safety** — IDE knows query return types (`List[User]`, not `List[Any]`)
- **Runtime validation** — Pydantic validates every row from the database
- **Cross-database** — Works with PostgreSQL, SQLite, MySQL via SQLAlchemy
- **No ORM magic** — Decoupled tables and models, explicit queries only

## Installation

```bash
pip install pyreact_start

# With database drivers
pip install pyreact_start[postgres]  # PostgreSQL with psycopg3
pip install pyreact_start[async]     # Async support with aiosqlite/asyncpg
```

## Quick Start

```python
from sqlalchemy import MetaData, Table, Column, Integer, String, select
from pydantic import BaseModel
from pyreact_start.db import Database, query, TypedQuery

# 1. Define table (SQLAlchemy Core)
metadata = MetaData()
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('email', String),
)

# 2. Define result model (Pydantic)
class User(BaseModel):
    id: int
    name: str
    email: str

# 3. Create typed query function (Option A - recommended)
def get_user(user_id: int) -> TypedQuery[User]:
    return query(User, select(users).where(users.c.id == user_id))

# 4. Execute with full type safety
db = Database("sqlite:///app.db")

with db.connection() as conn:
    user = conn.one(get_user(42))  # IDE knows: user is User
    print(user.name)               # Autocomplete works!
```

## Query Methods

pyreact_start.db provides explicit query methods:

| Method | Returns | Raises |
|--------|---------|--------|
| `one(query)` | Single `T` | `NotFoundError` (0 rows), `TooManyRowsError` (>1) |
| `maybe_one(query)` | `T \| None` | `TooManyRowsError` (>1) |
| `many(query)` | `List[T]` (1+) | `NotFoundError` (0 rows) |
| `any(query)` | `List[T]` (0+) | Never (for count) |

## Async Support

```python
from pyreact_start.db import AsyncDatabase, query

db = AsyncDatabase("sqlite+aiosqlite:///app.db")

async with db.connection() as conn:
    user = await conn.one(get_user(42))
    users = await conn.any(query(User, select(users)))
```

## Transactions

```python
# Auto-commits on success, rolls back on exception
with db.transaction() as conn:
    conn.one(create_user("Alice"))
    conn.one(create_user("Bob"))
    # Both committed together
```

## Performance: Skip Validation

For bulk operations where you trust the data:

```python
# Bypass Pydantic validation (constructs without checking)
users = conn.any(query, skip_validation=True)
```

## Philosophy

This DB adapter differs from SQLModel/ORMs:

| Aspect | SQLModel | pyreact_start.db |
|--------|----------|--------|
| Philosophy | One class = table + model | Tables and models are separate |
| State | Connected objects tracked by Session | Disconnected data (just Pydantic) |
| N+1 Problem | Possible (lazy loading) | Impossible (no magic) |

## License

MIT
