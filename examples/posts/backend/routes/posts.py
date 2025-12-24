"""Posts routes - CRUD operations."""

from fastapi import APIRouter, Request, Form
from pydantic import BaseModel
from sqlalchemy import select, insert, delete
from pyreact_start import Inertia
from pyreact_start.db import query

from backend.db.schema import posts
from backend.main import db, inertia

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


@router.post("/create")
async def create_post(request: Request, title: str = Form(...), body: str = Form(...)):
    """Create a new post."""
    with db.transaction() as conn:
        conn.execute(insert(posts).values(title=title, body=body))
    
    # Redirect to posts list
    return await inertia.render("Posts/Index", {
        "posts": [],
        "flash": {"success": "Post created!"}
    }, request)


@router.post("/{post_id}/delete")
async def delete_post(request: Request, post_id: int):
    """Delete a post."""
    with db.transaction() as conn:
        conn.execute(delete(posts).where(posts.c.id == post_id))
    
    return await inertia.render("Posts/Index", {
        "posts": [],
        "flash": {"success": "Post deleted!"}
    }, request)
