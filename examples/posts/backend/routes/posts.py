"""Posts routes - CRUD operations."""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from starlette.responses import RedirectResponse
from vegabase.db import query

from backend.db.schema import posts
from backend.initial import db, react

router = APIRouter(prefix="/posts", tags=["posts"])


class Post(BaseModel):
    """Post model for validation."""

    id: int
    title: str
    body: str


@router.get("")
@react.page("Posts/Index")
async def list_posts(request: Request):
    """List all posts."""
    with db.connection() as conn:
        all_posts = conn.all(query(Post, select(posts)))

    return {"posts": all_posts}


@router.get("/create")
@react.page("Posts/Create")
async def create_post_form(request: Request):
    """Show create post form."""
    return {}


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
    react.flash(request, "Post created successfully!", type="success")
    return RedirectResponse(url="/posts", status_code=303)


@router.post("/{post_id}/delete")
async def delete_post(request: Request, post_id: int):
    """Delete a post."""
    with db.transaction() as conn:
        conn.execute(delete(posts).where(posts.c.id == post_id))

    # Set flash message and redirect
    react.flash(request, "Post deleted successfully!", type="success")
    return RedirectResponse(url="/posts", status_code=303)
