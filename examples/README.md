# Examples

This directory contains example applications built with PyReact Start.

## Available Examples

| Example | Description |
|---------|-------------|
| [basic-app](./basic-app/) | Minimal "Hello World" — single page, no database |
| [tasks-app](./tasks-app/) | Full CRUD application with SQLite and Tailwind |

## Running an Example

Each example is a standalone project. To run one:

```bash
cd examples/tasks-app

# Install dependencies
pip install pyreact-start
bun install

# Start development
pyreact dev           # Terminal 1: frontend + SSR
python -m backend.main # Terminal 2: FastAPI backend
```

## Creating Your Own App

Use `basic-app` as a starting template:

```bash
cp -r examples/basic-app my-new-app
cd my-new-app
```
