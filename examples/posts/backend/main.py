"""Posts example - PyReact Start backend."""

import pathlib

from fastapi import Request
from fastapi.staticfiles import StaticFiles

from backend.initial import app, inertia
from backend.routes import posts

# Mount static files
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(posts.router)


@app.get("/")
async def home(request: Request):
    return await inertia.render(
        "Home", {"message": "Welcome to Posts Example!"}, request
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
