# vegabase: Bun + FastAPI + Inertia + Tailwind

## Development

### Prerequisites

- [Bun](https://bun.sh) (v1.0+)
- Python 3.10+
- `pip` dependencies installed (`fastapi`, `uvicorn`, `requests`)

### Setup

1. Install frontend dependencies:

   ```bash
   bun install
   cd frontend && bun install
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup database:
   ```bash
   vegabase db apply   # Creates tables
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
bun run dev
```

**Terminal 2: FastAPI Backend**
Runs the Python server (port 8000) which handles:

- API endpoints
- SSR requests to the Bun dev server
- Serving the HTML shell

```bash
# Make sure you are in the root directory
export APP_ENV=development
python -m backend.main
```

Access the app at `http://localhost:8000`

---

## Production

### Building

1. Build the client and SSR bundles:
   ```bash
   bun run build
   ```
   This generates:
   - `static/dist/client.js` (Client bundle)
   - `static/dist/client.css` (Tailwind CSS)
   - `backend/ssr.js` (SSR Server bundle)
   - `frontend/pages_map.js` (Generated page map)

### Running in Production

1. Start the SSR Server:

   ```bash
   nohup bun run start:ssr > ssr.log 2>&1 &
   ```

2. Start the FastAPI Server:
   ```bash
   # Set APP_ENV to production to serve assets from static/dist instead of localhost:3001
   export APP_ENV=production
   python -m backend.main
   ```

## Deployment Artifacts

To deploy to production, you only need these files/folders:

1. **Backend Code**: `backend/main.py`
2. **SSR Bundle**: `backend/ssr.js`
3. **Static Assets**: `static/dist/`
4. **Python Deps**: `pyproject.toml` (managed with `uv`)

You do **not** need `node_modules`, `frontend/`, `lib/`, or source TypeScript files in the production environment.

## Project Structure

- `backend/`: FastAPI application and generated SSR bundle
- `frontend/`: React source code
  - `pages/`: Inertia pages (auto-discovered)
  - `layouts/`: Shared layouts
  - `components/`: Reusable React components
- `lib/`: Extracted libraries
  - `python/vegabase/`: Inertia.js integration for FastAPI
  - `js/vegabase/`: Build and dev CLI tooling
- `static/dist/`: Generated client assets (not committed)
