# Basic App

A minimal Vegabase app example — single page, no database.

## Setup

```bash
pip install vegabase
bun install
```

## Development

```bash
# Terminal 1: Asset & SSR Server
vegabase dev bun

# Terminal 2: FastAPI Backend
vegabase dev py
```

Visit `http://localhost:8000`

### Ports
You can specify custom ports if needed:
```bash
vegabase dev bun --port 4001
vegabase dev py --port 8001
```

## Production

```bash
# Build assets
vegabase build
# Start SSR Server
nohup vegabase start bun > ssr.log 2>&1 &
# Start Backend
vegabase start py
