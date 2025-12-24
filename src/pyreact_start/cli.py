import os
import sys
import subprocess
import shutil
import importlib.util
from pathlib import Path


def init_project(project_name: str | None = None, with_db: bool = False):
    """
    Scaffold a new PyReact project.
    
    Args:
        project_name: Name of the project (creates new directory if provided)
        with_db: If True, include database schema scaffolding
    """
    if project_name:
        target_dir = Path.cwd() / project_name
        if target_dir.exists() and any(target_dir.iterdir()):
            print(f"❌ Error: Directory '{project_name}' already exists and is not empty.")
            sys.exit(1)
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = Path.cwd()
        project_name = target_dir.name

    print(f"🚀 Creating PyReact project '{project_name}'...\n")

    # Create directory structure
    (target_dir / "backend").mkdir(exist_ok=True)
    (target_dir / "frontend" / "pages").mkdir(parents=True, exist_ok=True)
    (target_dir / "static").mkdir(exist_ok=True)
    
    if with_db:
        (target_dir / "backend" / "db").mkdir(exist_ok=True)

    # Generate pyproject.toml
    db_deps = ""
    if with_db:
        db_deps = """
[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.0.0"]
"""
    
    pyproject_toml = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A PyReact Start app"
requires-python = ">=3.11"
dependencies = [
    "pyreact-start",
    "fastapi>=0.115.8",
    "uvicorn>=0.34.0",
]
{db_deps}"""

    # Generate package.json
    package_json = f"""{{
    "name": "{project_name}",
    "type": "module",
    "private": true,
    "dependencies": {{
        "@inertiajs/react": "^2.2.18",
        "react": "^19.2.0",
        "react-dom": "^19.2.0"
    }},
    "devDependencies": {{
        "@types/bun": "latest",
        "bun-plugin-tailwind": "^0.1.2",
        "tailwindcss": "^4.1.17"
    }}
}}
"""

    # Generate backend/__init__.py
    backend_init = ""

    # Generate backend/main.py (with db import if enabled)
    if with_db:
        backend_main = f'''"""{project_name} - PyReact Start backend."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pyreact_start import Inertia
from pyreact_start.db import Database, apply
from backend.db.schema import DATABASE_URL, metadata
import pathlib

app = FastAPI()

# Initialize database
db = Database(DATABASE_URL)

# Auto-sync schema in development (remove in production)
apply(db.engine, metadata)

# Initialize Inertia
inertia = Inertia(app)

# Mount static files (create static dir if it doesn't exist)
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return await inertia.render("Home", {{"message": "Hello from PyReact!"}}, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
'''
    else:
        backend_main = f'''"""{project_name} - PyReact Start backend."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pyreact_start import Inertia
import pathlib

app = FastAPI()

# Initialize Inertia
inertia = Inertia(app)

# Mount static files (create static dir if it doesn't exist)
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return await inertia.render("Home", {{"message": "Hello from PyReact!"}}, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
'''

    # Generate frontend/styles.css
    styles_css = '@import "tailwindcss";\n'

    # Generate frontend/pages/Home.jsx
    home_jsx = '''export default function Home({ message }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 shadow-2xl text-center">
                <h1 className="text-5xl font-bold text-white mb-4">
                    🚀 PyReact Start
                </h1>
                <p className="text-xl text-white/80">
                    {message}
                </p>
            </div>
        </div>
    );
}
'''

    # Generate db/schema.py (if with_db enabled)
    db_schema = '''"""
Database schema definition.

Define your tables here using SQLAlchemy Core.
Run `pyreact db plan` to preview changes and `pyreact db apply` to apply them.
"""

import os
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, DateTime, func

# Database connection URL (use environment variable in production)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

# SQLAlchemy MetaData - all tables are registered here
metadata = MetaData()

# Example table - modify or replace with your own
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), unique=True, nullable=False),
    Column("name", String(100), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)

# Add more tables here...
# posts = Table(
#     "posts",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("title", String(200), nullable=False),
#     Column("user_id", Integer, nullable=False),
# )
'''

    # Write all files
    (target_dir / "pyproject.toml").write_text(pyproject_toml)
    (target_dir / "package.json").write_text(package_json)
    (target_dir / "backend" / "__init__.py").write_text(backend_init)
    (target_dir / "backend" / "main.py").write_text(backend_main)
    (target_dir / "frontend" / "styles.css").write_text(styles_css)
    (target_dir / "frontend" / "pages" / "Home.jsx").write_text(home_jsx)
    
    if with_db:
        (target_dir / "backend" / "db" / "__init__.py").write_text("")
        (target_dir / "backend" / "db" / "schema.py").write_text(db_schema)

    print("📁 Created project structure:")
    print("   backend/")
    print("   ├── __init__.py")
    print("   └── main.py")
    if with_db:
        print("   │   db/")
        print("   │   ├── __init__.py")
        print("   │   └── schema.py")
    print("   frontend/")
    print("   ├── pages/")
    print("   │   └── Home.jsx")
    print("   └── styles.css")
    print("   static/")
    print("   package.json")
    print("   pyproject.toml")
    print("")
    print(f"✅ Created PyReact project '{project_name}'")
    if with_db:
        print("   (with database support)")
    print("")
    print("Next steps:")
    if project_name != Path.cwd().name:
        print(f"  cd {project_name}")
    print("  uv sync          # Install Python dependencies")
    print("  bun install      # Install JS dependencies")
    if with_db:
        print("  pyreact db apply # Create database tables")
    print("  pyreact dev      # Start development server")


def load_schema():
    """
    Load metadata and DATABASE_URL from db/schema.py by convention.
    
    Returns:
        Tuple of (database_url, metadata)
    """
    schema_path = Path.cwd() / "backend" / "db" / "schema.py"
    
    if not schema_path.exists():
        print("❌ Error: backend/db/schema.py not found")
        print("")
        print("Create backend/db/schema.py with your database schema:")
        print("")
        print("  from sqlalchemy import MetaData, Table, Column, Integer, String")
        print("")
        print('  DATABASE_URL = "sqlite:///app.db"  # or from env')
        print("  metadata = MetaData()")
        print("  users = Table('users', metadata,")
        print("      Column('id', Integer, primary_key=True),")
        print("      Column('name', String(100)),")
        print("  )")
        sys.exit(1)
    
    # Add the current directory to sys.path so imports work
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))
    
    # Import the schema module dynamically
    spec = importlib.util.spec_from_file_location("backend.db.schema", schema_path)
    if spec is None or spec.loader is None:
        print("❌ Error: Could not load backend/db/schema.py")
        sys.exit(1)
    
    schema = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(schema)
    except Exception as e:
        print(f"❌ Error loading backend/db/schema.py: {e}")
        sys.exit(1)
    
    # Check for required exports
    if not hasattr(schema, "DATABASE_URL"):
        print("❌ Error: backend/db/schema.py must export DATABASE_URL")
        sys.exit(1)
    
    if not hasattr(schema, "metadata"):
        print("❌ Error: backend/db/schema.py must export metadata (SQLAlchemy MetaData)")
        sys.exit(1)
    
    return schema.DATABASE_URL, schema.metadata


def db_plan():
    """Show planned schema changes without applying them."""
    from pyreact_start.db import Database, plan
    
    database_url, metadata = load_schema()
    db = Database(database_url)
    
    print(f"🔍 Comparing schema to database...")
    print(f"   Database: {database_url}")
    print("")
    
    changes = plan(db.engine, metadata)
    
    if not changes:
        print("✅ Schema is in sync - no changes needed")
        return
    
    print(f"📋 {len(changes)} change(s) planned:\n")
    for change in changes:
        print(f"   • {change}")
    
    print("")
    print("Run 'pyreact db apply' to apply these changes.")
    
    db.dispose()


def db_apply(force: bool = False):
    """Apply schema changes to the database."""
    from pyreact_start.db import Database, plan, apply
    
    database_url, metadata = load_schema()
    db = Database(database_url)
    
    print(f"🔍 Comparing schema to database...")
    print(f"   Database: {database_url}")
    print("")
    
    changes = plan(db.engine, metadata)
    
    if not changes:
        print("✅ Schema is in sync - no changes needed")
        db.dispose()
        return
    
    print(f"📋 {len(changes)} change(s) to apply:\n")
    for change in changes:
        print(f"   • {change}")
    print("")
    
    # Confirm unless --yes flag
    if not force:
        try:
            response = input("Apply these changes? [y/N] ").strip().lower()
            if response not in ("y", "yes"):
                print("Cancelled.")
                db.dispose()
                return
        except KeyboardInterrupt:
            print("\nCancelled.")
            db.dispose()
            return
    
    # Apply changes
    print("")
    print("⚡ Applying changes...")
    applied = apply(db.engine, metadata)
    
    print(f"✅ Applied {len(applied)} change(s)")
    
    db.dispose()


def db_command(args: list[str]):
    """Handle 'pyreact db' subcommands."""
    if not args:
        print("Usage: pyreact db <command>")
        print("")
        print("Commands:")
        print("  plan    Show planned schema changes (dry run)")
        print("  apply   Apply schema changes to the database")
        print("")
        print("Convention: Schema is loaded from db/schema.py")
        return
    
    subcommand = args[0]
    
    if subcommand == "plan":
        db_plan()
    elif subcommand == "apply":
        force = "--yes" in args or "-y" in args
        db_apply(force=force)
    else:
        print(f"❌ Unknown db command: {subcommand}")
        print("   Available: plan, apply")
        sys.exit(1)


def show_help():
    """Show CLI help."""
    print("PyReact Start CLI")
    print("")
    print("Commands:")
    print("  init [name]      Create a new PyReact project")
    print("    --db           Include database schema scaffolding")
    print("  dev              Start development server with hot reload")
    print("  build            Build for production")
    print("  ssr              Start the SSR server")
    print("  db               Manage database schema")
    print("")
    print("Database commands:")
    print("  db plan          Show planned schema changes (dry run)")
    print("  db apply         Apply schema changes to the database")


def main():
    """
    Main entry point for the 'pyreact' command.
    Handles 'init' command in Python, delegates others to TypeScript CLI.
    """
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    # Handle init command in Python (doesn't need Bun)
    if command == "init":
        # Parse init arguments
        args = sys.argv[2:]
        project_name = None
        with_db = "--db" in args
        
        # Find project name (first arg that doesn't start with --)
        for arg in args:
            if not arg.startswith("--"):
                project_name = arg
                break
        
        init_project(project_name, with_db=with_db)
        return

    # Handle db command in Python
    if command == "db":
        db_command(sys.argv[2:])
        return

    if command in ("--help", "-h", "help"):
        show_help()
        return

    # Delegate to TypeScript CLI for dev, build, ssr commands
    package_dir = os.path.dirname(os.path.abspath(__file__))
    cli_script = os.path.join(package_dir, "js", "src", "cli.ts")

    bun_exec = shutil.which("bun")
    if not bun_exec:
        print("❌ Error: 'bun' executable not found in PATH.")
        print("   Please install Bun: https://bun.sh")
        sys.exit(1)

    if not os.path.exists(cli_script):
        print(f"❌ Error: CLI script not found at {cli_script}")
        print("   This package may not be properly installed.")
        sys.exit(1)

    # Run the TypeScript CLI directly with Bun
    cmd = [bun_exec, "run", cli_script] + sys.argv[1:]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()

