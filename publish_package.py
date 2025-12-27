#!/usr/bin/env python3
"""
Build and publish script for vegabase.
Builds the Python package with TypeScript source included.

Usage:
    python publish_package.py          # Build only
    python publish_package.py --publish # Build and publish to PyPI
"""

import subprocess
import sys


def build_package():
    """Build the Python package using uv."""
    print("📦 Building Python package...")

    result = subprocess.run(["uv", "build"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Error building package:")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    print("✅ Package built successfully\n")


def publish_package():
    """Publish the package to PyPI."""
    print("🚀 Publishing to PyPI...")

    result = subprocess.run(["uv", "publish"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Error publishing package:")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    print("✅ Package published successfully\n")


if __name__ == "__main__":
    # Build package (ships TypeScript source, no bundling needed)
    build_package()

    # Optionally publish
    if "--publish" in sys.argv:
        publish_package()
        print("🎉 All done! Package is live on PyPI.")
    else:
        print("🎉 All done! Run with --publish to publish to PyPI.")
