# vegabase: Bun + FastAPI + Tanstack router + Tailwind

## Development

### Prerequisites

- [Bun](https://bun.sh) (v1.0+)
- Python 3.11+

### Setup

1. Install frontend dependencies:

   ```bash
   bun install
   ```

2. Install backend dependencies:

   ```bash
   uv sync
   ```

3. Setup database:

   ```bash
   uv run vegabase db apply   # Creates tables
   ```

   On first run, demo data (22 tickets, 8 tasks) is auto-seeded.
   To skip seeding: `SKIP_SEED=1 vegabase dev`

### Running in Development Mode

You need two terminal windows:

**Terminal 1: Asset Server & Bundler & SSR**
Runs the Bun dev server (port 3001) which handles:

- Hot reloading
- On-the-fly bundling of React components
- Tailwind CSS processing
- Serving client assets (`client.js`, `client.css`)
- **Server-Side Rendering (SSR)** via `/render` endpoint

```bash
vegabase dev bun
```

**Terminal 2: FastAPI Backend**
Runs the Python server (port 8000) which handles:

- API endpoints
- SSR requests to the Bun dev server
- Serving the HTML shell

```bash
vegabase dev py
```

Access the app at `http://localhost:8000`

---

## Production

### Building

1. Build the client and SSR bundles:
   ```bash
   vegabase build
   ```
   This generates:
   - `static/dist/client.js` (Client bundle)
   - `static/dist/client.css` (Tailwind CSS)
   - `.vegabase/ssr.js` (SSR Server bundle)
   - `frontend/pages_map.js` (Generated page map)

### Running in Production

1. Start the SSR Server:

   ```bash
   nohup vegabase start bun > ssr.log 2>&1 &
   ```

2. Start the FastAPI Server:
   ```bash
   # Set VEGABASE_APP_ENV to production (default)
   vegabase start py
   ```

## Deployment Artifacts

To deploy to production, you only need these files/folders:

1. **Backend Code**: `backend/`
2. **SSR Bundle**: `.vegabase/ssr.js`
3. **Static Assets**: `static/dist/`
4. **Python Deps**: `pyproject.toml` (managed with `uv`)

You do **not** need `node_modules`, `frontend/`, `lib/`, or source TypeScript files in the production environment.

## Project Structure

- `backend/`: FastAPI application and generated SSR bundle
- `frontend/`: React source code
  - `pages/`: Inertia pages (auto-discovered)
  - `layouts/`: Shared layouts
  - `components/`: Reusable React components
- `.vegabase/`: Generated entry files (not committed)
- `static/dist/`: Generated client assets (not committed)
