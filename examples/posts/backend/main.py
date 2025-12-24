"""Posts example - PyReact Start backend."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pyreact_start import Inertia
from pyreact_start.db import Database, apply
from backend.db.schema import DATABASE_URL, metadata
import pathlib

app = FastAPI()

# Initialize database
db = Database(DATABASE_URL)

# Auto-sync schema in development (remove in production)
apply(db.engine, metadata)

# Initialize Inertia
inertia = Inertia(app)

# Mount static files
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
from backend.routes import posts
app.include_router(posts.router)


@app.get("/")
async def home(request: Request):
    return await inertia.render("Home", {"message": "Welcome to Posts Example!"}, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
