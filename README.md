# PyReact Start

**Full-stack React + Python with zero configuration.**

Build modern React applications powered by FastAPI, Bun, Inertia.js, and Tailwind CSS — all from a single `pip install`.

## Motivation

When building React apps with Python, you're stuck with tough choices:

- **SPA-only**: You have an empty shell, and React takes over in the browser. No SEO, slow initial loads, and you still need to build a REST/GraphQL API.
- **Jinja + Islands**: Server-render with templates, then sprinkle React components for interactivity. But now you're thinking in two different worlds. And coordinating state across islands is not easy.

JavaScript developers use full stack frameworks like Next.js — full SSR, hydration, and seamless client/server data flow. Most python developers don't want to leave python ecosystem for the backend needs, and many want to use react for the frontend.

**PyReact Start aims to solve this by providing a zero-config way to build full-stack React + Python applications.** Your FastAPI routes render React components directly. Full SSR, full hydration, no API layer to build. It's a thin wrapper around Inertia.js and FastAPI. It assumes bun runtime so it can provide zero config experience.

- 🚀 **Zero Config**: Just install and run. Handles TS, TSX/JSX, CSS bundling along with Tailwind support out of the box.
- 🐍 **Python-First**: FastAPI backend with Python's full ecosystem.
- ⚛️ **Modern React**: React 19 with server-side rendering out of the box.
- ⚡ **Bun-Powered**: Lightning-fast bundling and SSR performance.


> **Requirements**:
> - [Bun](https://bun.sh) v1.0+ must be installed
> - Your project needs a `package.json` with React and Inertia dependencies

## Quick Start

### 1. Setup a new project

```bash
mkdir my-app && cd my-app

# Create pyproject.toml with Python dependencies
cat > pyproject.toml << 'EOF'
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pyreact-start",
    "fastapi",
    "uvicorn",
]
EOF

# Create package.json with JS dependencies
cat > package.json << 'EOF'
{
  "name": "my-app",
  "type": "module",
  "private": true,
  "dependencies": {
    "@inertiajs/react": "^2.2.18",
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "bun-plugin-tailwind": "^0.1.2",
    "tailwindcss": "^4.1.17"
  }
}
EOF

# Install dependencies
uv sync
bun install

# Create directories
mkdir -p backend frontend/pages static
touch backend/__init__.py
```

### 2. Create your FastAPI backend

```python
# backend/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pyreact_start import Inertia

app = FastAPI()
inertia = Inertia(app)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(request: Request):
    return await inertia.render("Home", {"message": "Hello!"}, request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
```

### 3. Create your first page

```jsx
// frontend/pages/Home.jsx
export default function Home({ message }) {
  return <h1>{message}</h1>;
}
```

```css
/* frontend/styles.css */
@import "tailwindcss";
```

### 4. Run!

```bash
# Terminal 1: Frontend dev server
pyreact dev

# Terminal 2: FastAPI backend
APP_ENV=development python -m backend.main
```

Visit `http://localhost:8000` 🎉

## Project Structure

```
my-app/
├── backend/
│   └── main.py           # FastAPI application
├── frontend/
│   ├── pages/            # React pages (auto-discovered)
│   ├── layouts/          # Shared layouts (optional)
│   ├── components/       # Reusable components (optional)
│   └── styles.css        # Tailwind entry point
├── static/dist/          # Generated assets (gitignored)
├── .pyreact/             # Generated entry files (gitignored)
├── package.json          # JS dependencies
└── pyproject.toml        # Python dependencies
```

The `.pyreact/` directory contains auto-generated files:
- `pages.js` — Page map (scanned from `frontend/pages/`)
- `client.jsx` — Client-side entry point
- `ssr.jsx` — Server-side rendering entry point

## Commands

| Command        | Description                                      |
| -------------- | ------------------------------------------------ |
| `pyreact dev`  | Start dev server with hot reloading              |
| `pyreact build`| Build optimized production bundles               |
| `pyreact ssr`  | Start the SSR server for production              |

## Production

```bash
# Build optimized bundles
pyreact build

# Start the SSR server (background)
pyreact ssr &

# Start the FastAPI server
APP_ENV=production python -m backend.main
```

## How It Works

1. **Auto-generated Entry Points**: When you run `pyreact dev` or `pyreact build`, the CLI generates entry files in `.pyreact/` that wire up your pages.
2. **Page Discovery**: All `.jsx` files in `frontend/pages/` are automatically discovered and mapped.
3. **Inertia.js Integration**: Your FastAPI routes render React components directly, with automatic SSR.
4. **Tailwind CSS**: Styles are processed via `bun-plugin-tailwind` during bundling.

## Requirements

- Python 3.11+
- [Bun](https://bun.sh) v1.0+

## Examples

See the [examples/](./examples) directory:

- **[basic-app](./examples/basic-app/)** — Minimal single-page example
- **[tasks-app](./examples/tasks-app/)** — Complex multi-page app with authentication with client side routing.

## License

MIT
