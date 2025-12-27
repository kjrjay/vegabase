"""Minimal PyReact Start backend."""

import pathlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from vegabase import Inertia

app = FastAPI()

# Initialize Inertia
inertia = Inertia(app)

# Mount static files (create static dir if it doesn't exist)
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return await inertia.render("Home", {"message": "Hello from PyReact!"}, request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
