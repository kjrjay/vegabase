"""Posts routes - CRUD operations."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from pyreact_start.db import query
from sqlalchemy import delete, insert, select

from backend.db.schema import posts
from backend.initial import db, inertia

router = APIRouter(prefix="/posts", tags=["posts"])


class Post(BaseModel):
    """Post model for validation."""

    id: int
    title: str
    body: str


@router.get("")
async def list_posts(request: Request):
    """List all posts."""
    with db.connection() as conn:
        all_posts = conn.any(query(Post, select(posts)))

    return await inertia.render("Posts/Index", {"posts": all_posts}, request)


@router.get("/create")
async def create_post_form(request: Request):
    """Show create post form."""
    return await inertia.render("Posts/Create", {}, request)


class PostCreate(BaseModel):
    """Input model for creating a post."""

    title: str
    body: str


@router.post("/create")
async def create_post(request: Request, data: PostCreate):
    """Create a new post."""
    with db.transaction() as conn:
        conn.execute(insert(posts).values(title=data.title, body=data.body))

    # Set flash message and redirect
    inertia.flash(request, "Post created successfully!", type="success")
    from starlette.responses import RedirectResponse

    return RedirectResponse(url="/posts", status_code=303)


@router.post("/{post_id}/delete")
async def delete_post(request: Request, post_id: int):
    """Delete a post."""
    with db.transaction() as conn:
        conn.execute(delete(posts).where(posts.c.id == post_id))

    # Set flash message and redirect
    inertia.flash(request, "Post deleted successfully!", type="success")
    from starlette.responses import RedirectResponse

    return RedirectResponse(url="/posts", status_code=303)
