"""Minimal Vegabase backend."""

import pathlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from vegabase import ReactRenderer, TimingMiddleware

app = FastAPI()
app.add_middleware(TimingMiddleware)

# Initialize ReactRenderer
react = ReactRenderer(app)

# Mount static files (create static dir if it doesn't exist)
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
@react.page("Home")
async def home(request: Request):
    return {"message": "Hello from Vegabase!"}
