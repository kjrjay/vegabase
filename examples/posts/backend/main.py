"""Posts example - Vegabase backend."""

import pathlib

from fastapi import Request
from fastapi.staticfiles import StaticFiles

from backend.initial import app, react
from backend.routes import posts

# Mount static files
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(posts.router)


@app.get("/")
@react.page("Home")
async def home(request: Request):
    return {"message": "Welcome to Posts Example!"}
