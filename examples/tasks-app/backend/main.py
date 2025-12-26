import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from pyreact_start import Inertia

from . import db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    await db.init_db()
    yield
    # Shutdown (nothing to do)


app = FastAPI(lifespan=lifespan)

# Add session middleware
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)  # type: ignore[arg-type]

# Initialize Inertia
inertia = Inertia(app)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Auth helper
async def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        user = await db.get_user_by_id(user_id)
        if user:
            # Use helper to convert to public dict (no password hash)
            return db.user_to_public(user)
    return None


@app.get("/")
async def root(request: Request):
    user = await get_current_user(request)
    return await inertia.render(
        "Dashboard",
        {"user": user, "data": {"message": "Hello from FastAPI + Bun + Inertia!"}},
        request,
    )


# Login/Logout
@app.get("/login")
async def login_page(request: Request):
    # If already logged in, redirect to dashboard
    if await get_current_user(request):
        return Response(status_code=303, headers={"Location": "/"})
    return await inertia.render("Login", {}, request)


@app.post("/login")
async def login(request: Request):
    import json

    body = await request.body()
    data = json.loads(body.decode())
    username = data.get("username")
    password = data.get("password")

    user = await db.verify_password(username, password)
    if user:
        request.session["user_id"] = user.id
        return Response(status_code=303, headers={"Location": "/"})
    else:
        # In production, use Inertia's error handling
        return Response(status_code=401, content="Invalid credentials")


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return Response(status_code=303, headers={"Location": "/"})


# Protected routes
@app.get("/tasks")
async def tasks_index(request: Request):
    user = await get_current_user(request)
    if not user:
        return Response(status_code=303, headers={"Location": "/login"})

    tasks = await db.get_all_tasks()
    return await inertia.render("Tasks/Index", {"user": user, "tasks": tasks}, request)


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    completed: bool


@app.post("/tasks")
async def create_task(task: TaskCreate):
    await db.add_task(task.title)
    return Response(status_code=303, headers={"Location": "/tasks"})


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    await db.update_task(task_id, task.completed)
    return Response(status_code=303, headers={"Location": "/tasks"})


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    await db.delete_task(task_id)
    return Response(status_code=303, headers={"Location": "/tasks"})


@app.get("/tickets")
async def tickets_index(request: Request):
    user = await get_current_user(request)
    if not user:
        return Response(status_code=303, headers={"Location": "/login"})

    tickets = await db.get_all_tickets()
    return await inertia.render(
        "Tickets/Index", {"user": user, "tickets": tickets}, request
    )


@app.post("/tickets")
async def create_ticket(ticket: dict):
    title = ticket.get("title", "Untitled")
    description = ticket.get("description", "")
    await db.add_ticket(title, description)
    return Response(status_code=303, headers={"Location": "/tickets"})


@app.get("/tickets/{ticket_id}")
async def show_ticket(ticket_id: int, request: Request):
    user = await get_current_user(request)
    if not user:
        return Response(status_code=303, headers={"Location": "/login"})

    ticket = await db.get_ticket(ticket_id)
    if not ticket:
        return Response(status_code=404)
    return await inertia.render(
        "Tickets/Show", {"user": user, "ticket": ticket}, request
    )


@app.put("/tickets/{ticket_id}")
async def update_ticket_endpoint(ticket_id: int, ticket: dict):
    await db.update_ticket(ticket_id, status=ticket.get("status"))
    return Response(status_code=303, headers={"Location": f"/tickets/{ticket_id}"})


@app.delete("/tickets/{ticket_id}")
async def delete_ticket_endpoint(ticket_id: int):
    await db.delete_ticket(ticket_id)
    return Response(status_code=303, headers={"Location": "/tickets"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
