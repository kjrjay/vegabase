# Vegabase

**Full-stack React + Python with zero configuration.**

Build modern React applications powered by FastAPI, Bun, TanStack Router, and Tailwind CSS — all from a single `pip install`.

## Motivation

When building React apps with Python, you typically have two choices:

- **SPA-only**: An empty HTML shell, React takes over in the browser. No SEO, slow initial loads, and you still need to build a REST/GraphQL API.
- **Jinja + Islands**: Server-render with templates, sprinkle React for interactivity. But you're constantly juggling two mental models.

Full-stack JS frameworks like Next and TanStack have SSR, hydration, and flexible rendering modes. Vegabase brings this experience to Python — use Python for backend logic, JavaScript for rendering html.

## Features

- 🚀 **Zero Config**: Just install and run. Handles TS, TSX/JSX, CSS bundling with Tailwind support.
- 🐍 **Python-First**: FastAPI backend with Python's full ecosystem.
- ⚛️ **Modern React**: React 19 with server-side rendering out of the box.
- ⚡ **Bun-Powered**: Lightning-fast bundling and SSR performance.
- 🗄️ **Type-Safe Database**: Built-in database module with Pydantic validation.
- 🎨 **Flexible Rendering**: SSR, client-only, ISR caching, or static HTML per-page.

> **Requirements**:
> - [Bun](https://bun.sh) v1.0+ must be installed
> - Python 3.11+

## Quick Start

```bash
# Create a new project with uvx (no install needed)
uvx vegabase init my-app --example posts

cd my-app
uv sync && bun install

# Terminal 1: Frontend dev server
vegabase dev bun

# Terminal 2: Backend
vegabase dev py
```

Visit `http://localhost:8000` 🎉

## CLI Commands

| Command | Description |
|---------|-------------|
| `vegabase init` | Create a new project |
| `vegabase dev bun` | Start Bun dev server (SSR + hot reload) |
| `vegabase dev py` | Start Python dev server |
| `vegabase build` | Build optimized production bundles |
| `vegabase start bun` | Start SSR server for production |
| `vegabase start py` | Start Python server for production |
| `vegabase db plan` | Preview database schema changes |
| `vegabase db apply` | Apply schema changes to database |

### Init Options

```bash
vegabase init --name my-app              # Create empty project
vegabase init --name my-app --example posts  # Start from posts example
vegabase init --name my-app --db sqlite      # Include SQLite setup
vegabase init --name my-app --db postgres    # Include PostgreSQL setup
```

## Rendering Modes

Control how each page is rendered:

```python
from vegabase import ReactRenderer

react = ReactRenderer(app)

# Default: Server-side rendering
await react.render("Home", props, request, mode="ssr")

# Client-only: Skip SSR, render in browser
await react.render("Dashboard", props, request, mode="client")

# Cached (ISR): Cache for 60 seconds
await react.render("Posts/Index", props, request, mode="cached", revalidate=60)

# Static: Pure HTML, no JavaScript bundle
await react.render("About", props, request, mode="static")
```

| Mode | SSR | Hydration | Use Case |
|------|-----|-----------|----------|
| `ssr` | ✅ | ✅ | Default, SEO-important pages |
| `client` | ❌ | ✅ | Dashboards, authenticated pages |
| `cached` | ✅ | ✅ | Blog posts, product pages (ISR) |
| `static` | ✅ | ❌ | Landing pages, pure content |

## Flash Messages

Built-in flash message support:

```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="...")
react = ReactRenderer(app)

@app.post("/posts/create")
async def create_post(request: Request):
    # ... create post ...
    react.flash(request, "Post created!", type="success")
    return RedirectResponse(url="/posts", status_code=303)
```

Access in React:

```tsx
export default function Index({ flash }) {
  return (
    <div>
      {flash && <Alert type={flash.type}>{flash.message}</Alert>}
    </div>
  );
}
```

## Database Module

Type-safe database queries with Pydantic validation:

```python
from sqlalchemy import MetaData, Table, Column, Integer, String, select
from pydantic import BaseModel
from vegabase.db import Database, query

# Define schema
metadata = MetaData()
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('email', String),
)

# Define model
class User(BaseModel):
    id: int
    name: str
    email: str

# Query with full type safety
db = Database("sqlite:///app.db")

with db.connection() as conn:
    user = conn.one(query(User, select(users).where(users.c.id == 42)))
    print(user.name)  # IDE autocomplete works!
    
    all_users = conn.all(query(User, select(users)))  # Returns List[User]
```

### Query Methods

| Method | Returns | On Empty |
|--------|---------|----------|
| `one()` | Single `T` | Raises `NotFoundError` |
| `maybe_one()` | `T \| None` | Returns `None` |
| `many()` | `List[T]` | Raises `NotFoundError` |
| `all()` | `List[T]` | Returns `[]` |

### Async Support

```python
from vegabase.db import AsyncDatabase

db = AsyncDatabase("sqlite+aiosqlite:///app.db")

async with db.connection() as conn:
    users = await conn.all(query(User, select(users)))
```

### Schema Management

No migration files — just compare and apply:

```bash
vegabase db plan   # Preview changes
vegabase db apply  # Apply changes
```

## Configuration

Vegabase uses [Dynaconf](https://www.dynaconf.com/) for layered configuration with environment support.

### Settings Files

Create any of these in your project root (loaded in order, later overrides earlier):

```
settings.yaml          # Base settings
settings.toml          # Alternative format
.secrets.yaml          # Sensitive values (gitignored)
settings.local.yaml    # Local overrides (gitignored)
```

### Environment Layering

```yaml
# settings.yaml
default:
  DATABASE_URL: "sqlite:///app.db"

development:
  DEBUG: true

production:
  DATABASE_URL: "postgresql://..."
```

Switch environments with `VEGABASE_APP_ENV`:

```bash
VEGABASE_APP_ENV=production python -m backend.main
```

### Accessing Settings

```python
from vegabase import settings

print(settings.DATABASE_URL)
print(settings.get("OPTIONAL_KEY", default="fallback"))
```

All settings can be overridden via environment variables with `VEGABASE_` prefix:

```bash
VEGABASE_DATABASE_URL="postgresql://..." python -m backend.main
```

## Logging

Vegabase includes structured logging out of the box:

- **Request timing**: Every request logs method, path, status, and duration
- **Consistent format**: ISO timestamps across Python and Bun servers
- **Customizable**: Override via `LOGGING` in your settings file

Example output:

```
2026-01-04T21:09:01+0000 INFO vegabase.access GET /posts 200 45ms
2026-01-04T21:09:01+0000 INFO vegabase.access POST /posts/create 303 123ms
```

Customize logging in `settings.yaml`:

```yaml
default:
  LOGGING:
    dynaconf_merge: true  # Extend defaults instead of replacing
    root:
      level: DEBUG
```


## Production

```bash
# Build optimized bundles
vegabase build

# Start the SSR server (background)
vegabase start bun &

# Start the FastAPI server
vegabase start py
```

## Examples

See the [examples/](./examples) directory:

- **[basic-app](./examples/basic-app/)** — Minimal single-page example
- **[posts](./examples/posts/)** — CRUD app with flash messages and database
- **[ticketing](./examples/ticketing/)** — Full app with authentication, multi-page routing

## License

MIT
