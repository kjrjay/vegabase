# Vegabase app Examples

This directory contains example projects that can be used with `vegabase init --example`.

## Available Examples

| Example | Description |
|---------|-------------|
| `posts` | CRUD posts app with database, routes, and React pages |

## Usage

```bash
# Create a new project with the posts example
vegabase init my-app --example posts

# Then set up and run
cd my-app
uv sync
bun install
vegabase db apply
vegabase dev
```

## Creating New Examples

Each example is a complete project with:
- `pyproject.toml` - Python dependencies
- `package.json` - JavaScript dependencies
- `backend/` - FastAPI routes and database
- `frontend/` - React pages

Use `{{project_name}}` in config files for template substitution.
