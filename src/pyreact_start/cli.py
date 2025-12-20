import os
import sys
import subprocess
import shutil
from pathlib import Path


def init_project(project_name: str | None = None):
    """
    Scaffold a new PyReact project.
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

    # Generate pyproject.toml
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
"""

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

    # Generate backend/main.py
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

    # Write all files
    (target_dir / "pyproject.toml").write_text(pyproject_toml)
    (target_dir / "package.json").write_text(package_json)
    (target_dir / "backend" / "__init__.py").write_text(backend_init)
    (target_dir / "backend" / "main.py").write_text(backend_main)
    (target_dir / "frontend" / "styles.css").write_text(styles_css)
    (target_dir / "frontend" / "pages" / "Home.jsx").write_text(home_jsx)

    print("📁 Created project structure:")
    print("   backend/")
    print("   ├── __init__.py")
    print("   └── main.py")
    print("   frontend/")
    print("   ├── pages/")
    print("   │   └── Home.jsx")
    print("   └── styles.css")
    print("   static/")
    print("   package.json")
    print("   pyproject.toml")
    print("")
    print(f"✅ Created PyReact project '{project_name}'")
    print("")
    print("Next steps:")
    if project_name != Path.cwd().name:
        print(f"  cd {project_name}")
    print("  uv sync          # Install Python dependencies")
    print("  bun install      # Install JS dependencies")
    print("  pyreact dev      # Start development server")


def show_help():
    """Show CLI help."""
    print("PyReact Start CLI")
    print("")
    print("Commands:")
    print("  init [name]  Create a new PyReact project")
    print("  dev          Start development server with hot reload")
    print("  build        Build for production")
    print("  ssr          Start the SSR server")


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
        project_name = sys.argv[2] if len(sys.argv) > 2 else None
        init_project(project_name)
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
