import os
import sys
import subprocess
import shutil

def main():
    """
    Main entry point for the 'pyreact' command.
    Runs the TypeScript CLI directly with Bun.
    """
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
    # Dependencies (react, bun-plugin-tailwind, etc.) must be in the user's project
    cmd = [bun_exec, "run", cli_script] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    main()
