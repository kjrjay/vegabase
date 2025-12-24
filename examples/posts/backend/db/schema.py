"""
Database schema for posts example.
"""

import os
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, DateTime, func

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

metadata = MetaData()

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("body", Text, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)
