"""
User CRUD and authentication operations.
"""

import hashlib

from sqlalchemy import insert, select

from vegabase.db import query

from . import db
from .schema import User, users


async def get_user_by_username(username: str) -> User | None:
    """Get user by username."""
    async with db.connection() as conn:
        return await conn.maybe_one(
            query(User, select(users).where(users.c.username == username))
        )


async def get_user_by_id(user_id: int) -> User | None:
    """Get user by ID."""
    async with db.connection() as conn:
        return await conn.maybe_one(
            query(User, select(users).where(users.c.id == user_id))
        )


async def create_user(
    username: str, name: str, password: str, avatar_url: str | None = None
) -> int | None:
    """Create a new user with hashed password."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        async with db.transaction() as conn:
            result = await conn._conn.execute(
                insert(users).values(
                    username=username,
                    name=name,
                    password_hash=password_hash,
                    avatar_url=avatar_url,
                )
            )
            return result.lastrowid
    except Exception:
        return None


async def verify_password(username: str, password: str) -> User | None:
    """Verify user credentials."""
    user = await get_user_by_username(username)
    if not user:
        return None
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.password_hash == password_hash:
        return user
    return None


def user_to_public(user: User) -> dict:
    """Convert User to public dict (no password hash)."""
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "avatar_url": user.avatar_url,
    }
