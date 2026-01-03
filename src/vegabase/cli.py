import importlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

try:
    import click
except ImportError:
    print("❌ Error: 'click' is required. Please install vegabase with dependencies.")
    print("   pip install vegabase")
    sys.exit(1)

# GitHub repo for examples
EXAMPLES_REPO = "kjrjay/vegabase"
EXAMPLES_BRANCH = "main"


def download_example(example: str, target_dir: Path, project_name: str):
    """
    Download an example from GitHub and copy it to target_dir.

    Args:
        example: Name of the example (e.g., 'posts')
        target_dir: Directory to copy the example to
        project_name: Name of the project for template substitution
    """
    print(f"📦 Downloading example '{example}' from GitHub...")

    # Download the repo as a zip
    zip_url = (
        f"https://github.com/{EXAMPLES_REPO}/archive/refs/heads/{EXAMPLES_BRANCH}.zip"
    )

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            zip_path = tmp_path / "repo.zip"

            # Download zip
            urllib.request.urlretrieve(zip_url, zip_path)

            # Extract
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmp_path)

            # Find the example folder
            # Zip extracts to: vegabase-main/examples/posts/
            repo_name = EXAMPLES_REPO.split("/")[1]
            example_src = (
                tmp_path / f"{repo_name}-{EXAMPLES_BRANCH}" / "examples" / example
            )

            if not example_src.exists():
                print(f"❌ Example '{example}' not found in repository")
                print("   Available examples: posts")
                sys.exit(1)

            # Copy files to target, handling template substitution
            for src_file in example_src.rglob("*"):
                if src_file.is_file():
                    rel_path = src_file.relative_to(example_src)
                    dst_file = target_dir / rel_path

                    # Create parent directories
                    dst_file.parent.mkdir(parents=True, exist_ok=True)

                    # Read and substitute templates
                    content = src_file.read_text()
                    content = content.replace("{{project_name}}", project_name)

                    dst_file.write_text(content)

            print(f"✅ Downloaded example '{example}'")

    except urllib.error.URLError as e:
        print(f"❌ Failed to download: {e}")
        print("   Check your internet connection and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def init_project_structure(project_name: str | None = None, with_db: bool = False):
    """
    Scaffold a new Vegabase project.

    Args:
        project_name: Name of the project (creates new directory if provided)
        with_db: If True, include database schema scaffolding
    """
    if project_name:
        target_dir = Path.cwd() / project_name
        if target_dir.exists() and any(target_dir.iterdir()):
            print(
                f"❌ Error: Directory '{project_name}' already exists and is not empty."
            )
            sys.exit(1)
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = Path.cwd()
        project_name = target_dir.name

    print(f"🚀 Creating Vegabase project '{project_name}'...\n")

    # Create directory structure
    (target_dir / "backend").mkdir(exist_ok=True)
    (target_dir / "frontend" / "pages").mkdir(parents=True, exist_ok=True)
    (target_dir / "static").mkdir(exist_ok=True)

    if with_db:
        (target_dir / "backend" / "db").mkdir(exist_ok=True)

    # Generate pyproject.toml with opinionated defaults
    db_deps = ""
    db_core_dep = ""
    if with_db:
        db_core_dep = '\n    "sqlalchemy>=2.0.0",'
        db_deps = """
[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.0.0"]
"""

    pyproject_toml = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "A Vegabase app"
requires-python = ">=3.11"
dependencies = [
    "vegabase",
    "fastapi>=0.115.8",
    "uvicorn[standard]>=0.34.0",{db_core_dep}
]
{db_deps}
[dependency-groups]
dev = ["ruff>=0.8.0", "ty>=0.0.1a6"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.format]
quote-style = "double"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]
'''

    # Generate package.json with TypeScript and oxlint
    package_json = f'''{{
    "name": "{project_name}",
    "type": "module",
    "private": true,
    "scripts": {{
        "lint": "oxlint .",
        "format": "oxlint --fix .",
        "typecheck": "tsc --noEmit"
    }},
    "dependencies": {{
        "@tanstack/react-router": "^1.120.0",
        "react": "^19.2.0",
        "react-dom": "^19.2.0"
    }},
    "devDependencies": {{
        "@types/bun": "latest",
        "@types/react": "^19.0.0",
        "@types/react-dom": "^19.0.0",
        "bun-plugin-tailwind": "^0.1.2",
        "oxlint": "latest",
        "tailwindcss": "^4.1.17",
        "typescript": "^5.7.0"
    }}
}}
'''

    # Generate backend/__init__.py
    backend_init = ""

    if with_db:
        backend_main = f'''"""{project_name} - Vegabase backend."""

import pathlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from vegabase import ReactRenderer
from vegabase.db import Database, apply

from backend.db.schema import DATABASE_URL, metadata

app = FastAPI()

# Initialize database
db = Database(DATABASE_URL)

# Auto-sync schema in development (remove in production)
apply(db.engine, metadata)

# Initialize Renderer
react = ReactRenderer(app)

# Mount static files (create static dir if it doesn't exist)
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return await react.render("Home", {{"message": "Hello from Vegabase!"}}, request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
'''
    else:
        backend_main = f'''"""{project_name} - Vegabase backend."""

import pathlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from vegabase import ReactRenderer

app = FastAPI()

# Initialize Renderer
react = ReactRenderer(app)

# Mount static files (create static dir if it doesn't exist)
pathlib.Path("static/dist").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return await react.render("Home", {{"message": "Hello from Vegabase!"}}, request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
'''

    # Generate frontend/styles.css
    styles_css = '@import "tailwindcss";\n'

    # Generate tsconfig.json for TypeScript
    tsconfig_json = """{
    "compilerOptions": {
        "target": "ES2022",
        "module": "ESNext",
        "moduleResolution": "bundler",
        "jsx": "react-jsx",
        "strict": true,
        "noEmit": true,
        "skipLibCheck": true,
        "esModuleInterop": true,
        "allowSyntheticDefaultImports": true,
        "forceConsistentCasingInFileNames": true,
        "resolveJsonModule": true,
        "isolatedModules": true
    },
    "include": ["frontend/**/*"],
    "exclude": ["node_modules"]
}
"""

    # Generate frontend/pages/Home.tsx (TypeScript)
    home_tsx = """interface HomeProps {
    message: string;
}

export default function Home({ message }: HomeProps) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-12 shadow-2xl text-center">
                <h1 className="text-5xl font-bold text-white mb-4">
                    🚀 Vegabase
                </h1>
                <p className="text-xl text-white/80">
                    {message}
                </p>
            </div>
        </div>
    );
}
"""

    # Generate db/schema.py (if with_db enabled)
    db_schema = '''"""
Database schema definition.

Define your tables here using SQLAlchemy Core.
Run `vegabase db plan` to preview changes and `vegabase db apply` to apply them.
"""

import os

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, func

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
    (target_dir / "tsconfig.json").write_text(tsconfig_json)
    (target_dir / "backend" / "__init__.py").write_text(backend_init)
    (target_dir / "backend" / "main.py").write_text(backend_main)
    (target_dir / "frontend" / "styles.css").write_text(styles_css)
    (target_dir / "frontend" / "pages" / "Home.tsx").write_text(home_tsx)

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
    print("   │   └── Home.tsx")
    print("   └── styles.css")
    print("   static/")
    print("   package.json")
    print("   pyproject.toml")
    print("   tsconfig.json")
    print("")
    print(f"✅ Created Vegabase project '{project_name}'")
    if with_db:
        print("   (with database support)")
    print("")
    print("Next steps:")
    if project_name != Path.cwd().name:
        print(f"  cd {project_name}")
    print("  uv sync          # Install Python dependencies")
    print("  bun install      # Install JS dependencies")
    if with_db:
        print("  vegabase db apply # Create database tables")
    print("  vegabase dev      # Start development server")


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

    # Type assertions to help type checker understand the narrowing
    assert spec is not None
    assert spec.loader is not None

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
        print(
            "❌ Error: backend/db/schema.py must export metadata (SQLAlchemy MetaData)"
        )
        sys.exit(1)

    return schema.DATABASE_URL, schema.metadata


def extract_routes():
    """
    Extract routes from the user's Python app and save to .vegabase/routes.json.

    Assumes `backend.main` exports a `react` instance of ReactRenderer.
    """
    # Add current directory to path so we can import backend.main
    if str(Path.cwd()) not in sys.path:
        sys.path.insert(0, str(Path.cwd()))

    try:
        import importlib

        backend_main = importlib.import_module("backend.main")

        if not hasattr(backend_main, "react"):
            print(
                "❌ Error: backend.main must export 'react' (a ReactRenderer instance)"
            )
            sys.exit(1)

        react = backend_main.react
        output = react.save_routes()
        route_count = len(react._routes)
        print(f"📋 Extracted {route_count} route(s) → {output}")

    except ImportError as e:
        print(f"❌ Error: Could not import backend.main: {e}")
        print("   Make sure you are running this from your project root.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error extracting routes: {e}")
        sys.exit(1)


@click.group()
def main():
    """Vegabase CLI"""
    pass


@main.command()
@click.argument("name", required=False)
@click.option("--db", is_flag=True, help="Include database schema scaffolding")
@click.option("--example", help="Use an example template (e.g., posts)")
def init(name: str | None, db: bool, example: str | None):
    """Create a new Vegabase project"""
    if example:
        project_name = name or example
        target_dir = Path.cwd() / project_name
        if target_dir.exists() and any(target_dir.iterdir()):
            print(
                f"❌ Error: Directory '{project_name}' already exists and is not empty."
            )
            sys.exit(1)
        target_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"🚀 Creating Vegabase project '{project_name}' from example '{example}'...\n"
        )
        download_example(example, target_dir, project_name)

        print("")
        print(f"✅ Created Vegabase project '{project_name}'")
        print("")
        print("Next steps:")
        print(f"  cd {project_name}")
        print("  uv sync          # Install Python dependencies")
        print("  bun install      # Install JS dependencies")
        print("  vegabase db apply # Create database tables")
        print("  vegabase dev      # Start development server")
    else:
        init_project_structure(name, with_db=db)


def _start_python_server(
    port: int | None,
    is_dev: bool,
) -> None:
    """Helper to start Python server (dev or production)."""
    from vegabase.config import settings

    env = os.environ.copy()
    if port:
        env["PORT"] = str(port)

    # Determine which server URL to display
    if is_dev:
        server_url = settings.ASSETS_URL.replace("http://", "").replace("https://", "")
        server_type = "dev"
    else:
        server_url = (
            settings.SSR_URL.replace("http://", "")
            .replace("https://", "")
            .replace("/render", "")
        )
        server_type = "ssr"

    print(f"🌍 Environment: {settings.current_env}")
    print("🐍 Starting Python server...")
    print(f"   (Make sure bun {server_type} server is running at {server_url})")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(port) if port else "8000",
    ]

    # Add reload flag for dev mode
    if is_dev:
        cmd.append("--reload")

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


@main.command()
@click.argument("mode", type=click.Choice(["bun", "py"]))
@click.option("--port", type=int, help="Specify port")
def dev(mode: str, port: int | None):
    """Start development server"""
    # Extract routes from Python app before delegating
    extract_routes()

    if mode == "py":
        _start_python_server(port, is_dev=True)
    else:
        # Bun mode (Delegate to TS CLI)
        args = ["--port", str(port)] if port else []
        _run_bun_cli("dev", args)


@main.command()
@click.argument("mode", type=click.Choice(["bun", "py"]))
@click.option("--port", type=int, help="Specify port")
def start(mode: str, port: int | None):
    """Start production server"""
    if mode == "py":
        _start_python_server(port, is_dev=False)
    else:
        # Bun mode (Delegate to TS CLI)
        args = ["--port", str(port)] if port else []
        _run_bun_cli("start", args)


@main.command()
def build():
    """Build for production"""
    extract_routes()
    _run_bun_cli("build", [])


@main.group()
def db():
    """Manage database schema"""
    pass


@db.command()
def plan():
    """Show planned schema changes (dry run)"""
    from vegabase.db import Database
    from vegabase.db import plan as db_plan_func

    database_url, metadata = load_schema()
    db_conn = Database(database_url)

    print("🔍 Comparing schema to database...")
    print(f"   Database: {database_url}")
    print("")

    changes = db_plan_func(db_conn.engine, metadata)

    if not changes:
        print("✅ Schema is in sync - no changes needed")
        return

    print(f"📋 {len(changes)} change(s) planned:\n")
    for change in changes:
        print(f"   • {change}")

    print("")
    print("Run 'vegabase db apply' to apply these changes.")
    db_conn.dispose()


@db.command()
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def apply(yes: bool):
    """Apply schema changes to the database"""
    from vegabase.db import Database
    from vegabase.db import apply as db_apply_func
    from vegabase.db import plan as db_plan_func

    database_url, metadata = load_schema()
    db_conn = Database(database_url)

    print("🔍 Comparing schema to database...")
    print(f"   Database: {database_url}")
    print("")

    changes = db_plan_func(db_conn.engine, metadata)

    if not changes:
        print("✅ Schema is in sync - no changes needed")
        db_conn.dispose()
        return

    print(f"📋 {len(changes)} change(s) to apply:\n")
    for change in changes:
        print(f"   • {change}")
    print("")

    if not yes:
        try:
            response = input("Apply these changes? [y/N] ").strip().lower()
            if response not in ("y", "yes"):
                print("Cancelled.")
                db_conn.dispose()
                return
        except KeyboardInterrupt:
            print("\nCancelled.")
            db_conn.dispose()
            return

    print("")
    print("⚡ Applying changes...")
    applied = db_apply_func(db_conn.engine, metadata)
    print(f"✅ Applied {len(applied)} change(s)")
    db_conn.dispose()


def _run_bun_cli(command: str, args: list[str]):
    package_dir = os.path.dirname(os.path.abspath(__file__))
    cli_script = os.path.join(package_dir, "ts", "src", "cli.ts")

    bun_exec = shutil.which("bun")
    if not bun_exec:
        print("❌ Error: 'bun' executable not found in PATH.")
        print("   Please install Bun: https://bun.sh")
        sys.exit(1)

    if not os.path.exists(cli_script):
        print(f"❌ Error: CLI script not found at {cli_script}")
        print("   This package may not be properly installed.")
        sys.exit(1)

    cmd = [bun_exec, "run", cli_script, command] + args

    # Pass through environment variables (including PORT if set)
    env = os.environ.copy()

    # Extract port from args and set PORT env var for TS CLI
    # TS CLI currently doesn't parse --port flag, it reads process.env.PORT
    if "--port" in args:
        port_index = args.index("--port")
        if port_index + 1 < len(args):
            env["PORT"] = args[port_index + 1]

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
