import aiosqlite
import os

DB_PATH = "tasks.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                avatar_url TEXT,
                password_hash TEXT NOT NULL
            )
        ''')
        await conn.commit()

# Tasks CRUD
async def get_all_tasks():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM tasks') as cursor:
            tasks = await cursor.fetchall()
            return [dict(task) for task in tasks]

async def add_task(title):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute('INSERT INTO tasks (title, completed) VALUES (?, ?)', (title, False))
        await conn.commit()
        return cursor.lastrowid

async def update_task(task_id, completed):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
        await conn.commit()

async def delete_task(task_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        await conn.commit()

# Tickets CRUD
async def get_all_tickets():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM tickets ORDER BY created_at DESC') as cursor:
            tickets = await cursor.fetchall()
            return [dict(ticket) for ticket in tickets]

async def get_ticket(ticket_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)) as cursor:
            ticket = await cursor.fetchone()
            return dict(ticket) if ticket else None

async def add_ticket(title, description):
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            'INSERT INTO tickets (title, description, status) VALUES (?, ?, ?)',
            (title, description, 'open')
        )
        await conn.commit()
        return cursor.lastrowid

async def update_ticket(ticket_id, status=None, title=None, description=None):
    async with aiosqlite.connect(DB_PATH) as conn:
        if status:
            await conn.execute('UPDATE tickets SET status = ? WHERE id = ?', (status, ticket_id))
        if title:
            await conn.execute('UPDATE tickets SET title = ? WHERE id = ?', (title, ticket_id))
        if description:
            await conn.execute('UPDATE tickets SET description = ? WHERE id = ?', (description, ticket_id))
        await conn.commit()

async def delete_ticket(ticket_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        await conn.commit()

# Users/Auth
async def get_user_by_username(username):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM users WHERE username = ?', (username,)) as cursor:
            user = await cursor.fetchone()
            return dict(user) if user else None

async def get_user_by_id(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)) as cursor:
            user = await cursor.fetchone()
            return dict(user) if user else None

async def create_user(username, name, password, avatar_url=None):
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    async with aiosqlite.connect(DB_PATH) as conn:
        try:
            cursor = await conn.execute(
                'INSERT INTO users (username, name, password_hash, avatar_url) VALUES (?, ?, ?, ?)',
                (username, name, password_hash, avatar_url)
            )
            await conn.commit()
            return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None

async def verify_password(username, password):
    import hashlib
    user = await get_user_by_username(username)
    if not user:
        return None
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] == password_hash:
        return user
    return None
