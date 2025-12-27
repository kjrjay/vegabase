"""Shared application dependencies for FastAPI dependency injection."""

from fastapi import FastAPI
from vegabase import Inertia
from vegabase.db import Database, apply
from starlette.middleware.sessions import SessionMiddleware

from backend.db.schema import DATABASE_URL, metadata

# Initialize database once
db = Database(DATABASE_URL)
apply(db.engine, metadata)

app = FastAPI()

# Add session middleware for flash messages
# In production, use a secure secret from environment variables
app.add_middleware(SessionMiddleware, secret_key="change-this-in-production")  # type: ignore[arg-type]

inertia = Inertia(app)
