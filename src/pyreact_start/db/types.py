"""
Core type definitions for the library.

Provides TypedQuery[T] - the key abstraction binding SQL statements to Pydantic models.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select

# TypeVar bound to BaseModel for result type safety
T = TypeVar("T", bound=BaseModel)


class TypedQuery(Generic[T]):
    """
    Binds a SQLAlchemy Select statement to a Pydantic model type.

    This is the core abstraction that enables type-safe queries:
    - Static typing: IDE knows the return type
    - Runtime validation: Pydantic validates each row

    Example:
        ```python
        class User(BaseModel):
            id: int
            name: str

        query = typed(User, select(users))
        # query is TypedQuery[User]
        # conn.one(query) returns User
        ```
    """

    __slots__ = ("model", "statement")

    def __init__(self, model: type[T], statement: Select[Any]):
        self.model = model
        self.statement = statement

    def __repr__(self) -> str:
        return f"TypedQuery[{self.model.__name__}]({self.statement})"


def query(model: type[T], statement: Select[Any]) -> TypedQuery[T]:
    """
    Create a TypedQuery binding a Pydantic model to a SQL statement.

    Primary pattern: Use with query functions for type-safe parameters.

    Example:
        ```python
        def get_user(user_id: int) -> TypedQuery[User]:
            return query(User, select(users).where(users.c.id == user_id))

        user = conn.one(get_user(42))  # IDE knows: user is User
        ```

    Args:
        model: A Pydantic BaseModel subclass defining the row shape
        statement: A SQLAlchemy Select statement

    Returns:
        TypedQuery[T] that can be executed via Database connection methods
    """
    return TypedQuery(model, statement)

