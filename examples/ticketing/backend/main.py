import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from vegabase import ReactRenderer

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

# Initialize React renderer
react = ReactRenderer(app)

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
@react.page("Dashboard", mode="client", cache_time=60)
async def root(request: Request):
    user = await get_current_user(request)
    # Get real stats from database
    user_id = user["id"] if user else None
    stats = await db.get_dashboard_stats(user_id)
    # Get ticket history for chart (both weekly and monthly)
    weekly_history = await db.get_ticket_history("weekly")
    monthly_history = await db.get_ticket_history("monthly")
    return {
        "user": user,
        "taskStats": stats["tasks"],
        "ticketStats": stats["tickets"],
        "ticketHistory": {
            "weekly": weekly_history,
            "monthly": monthly_history,
        },
    }


# Login/Logout
@app.get("/login")
@react.page("Login")
async def login_page(request: Request):
    # If already logged in, redirect to dashboard
    if await get_current_user(request):
        return Response(status_code=303, headers={"Location": "/"})
    return {}


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
        return Response(status_code=401, content="Invalid credentials")


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return Response(status_code=303, headers={"Location": "/"})


@app.get("/tasks")
@react.page("Tasks/Index", mode="ssr", cache_time=30)
async def tasks_index(request: Request):
    user = await get_current_user(request)
    if not user:
        return Response(status_code=303, headers={"Location": "/login"})

    tasks = await db.get_tasks_for_user(user["id"])
    return {"user": user, "tasks": tasks}


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    completed: bool


@app.post("/tasks")
async def create_task(request: Request, task: TaskCreate):
    user = await get_current_user(request)
    if not user:
        return Response(status_code=401, content="Unauthorized")
    await db.add_task(user["id"], task.title)
    return Response(status_code=200)


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    await db.update_task(task_id, task.completed)
    return Response(status_code=200)


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    await db.delete_task(task_id)
    return Response(status_code=200)


@app.get("/tickets")
@react.page("Tickets/Index", mode="ssr")
async def tickets_index(request: Request):
    user = await get_current_user(request)
    tickets = await db.get_tickets_with_author()
    return {"user": user, "tickets": tickets}


@app.post("/tickets")
async def create_ticket(request: Request, ticket: dict):
    user = await get_current_user(request)
    if not user:
        return Response(status_code=401, content="Unauthorized")
    title = ticket.get("title", "Untitled")
    description = ticket.get("description", "")
    await db.add_ticket(user["id"], title, description)
    return Response(status_code=200)


@app.get("/tickets/{ticket_id}")
@react.page("Tickets/Show", mode="ssr")
async def show_ticket(ticket_id: int, request: Request):
    user = await get_current_user(request)
    ticket = await db.get_ticket(ticket_id)
    if not ticket:
        return Response(status_code=404)
    return {"user": user, "ticket": ticket}


@app.put("/tickets/{ticket_id}")
async def update_ticket_endpoint(ticket_id: int, ticket: dict):
    await db.update_ticket(ticket_id, status=ticket.get("status"))
    return Response(status_code=200)


@app.delete("/tickets/{ticket_id}")
async def delete_ticket_endpoint(ticket_id: int):
    await db.delete_ticket(ticket_id)
    return Response(status_code=200)


@app.get("/about")
@react.page("About", mode="static")
async def about(request: Request):
    """Static page - no JavaScript hydration."""
    return {}
