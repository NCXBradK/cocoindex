#!/usr/bin/env python3
"""
Build script for CocoIndex Standalone Watcher executable
Supports Windows, macOS, and Linux
"""

import os
import sys
import shutil
import argparse
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}")
        return False
    print(result.stdout)
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    # Check PyInstaller
    try:
        import PyInstaller

        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Install with: pip install pyinstaller")
        return False

    # Check watchdog
    try:
        import watchdog

        print(f"✓ Watchdog version: {watchdog.__version__}")
    except ImportError:
        print("✗ Watchdog not found. Install with: pip install watchdog")
        return False

    # Check cocoindex
    try:
        import cocoindex

        print(f"✓ CocoIndex found")
    except ImportError:
        print("✗ CocoIndex not found. Install with: pip install cocoindex")
        return False

    return True


def build_executable(output_dir="dist", clean=False):
    """Build the standalone executable."""
    project_root = Path(__file__).parent

    # Clean previous builds
    if clean and (project_root / "dist").exists():
        print("Cleaning previous builds...")
        shutil.rmtree(project_root / "dist")

    if clean and (project_root / "build").exists():
        shutil.rmtree(project_root / "build")

    # Create output directory
    output_path = project_root / output_dir
    output_path.mkdir(exist_ok=True)

    # Build command
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--console",
        "--name",
        "cocoindex-watcher",
        "--distpath",
        str(output_path),
        "standalone_watcher.py",
    ]

    # Platform-specific optimizations
    system = platform.system().lower()

    if system == "windows":
        # Windows-specific options
        cmd.extend(
            [
                "--add-data",
                "python/cocoindex;cocoindex",
                "--exclude-module",
                "tkinter",
                "--exclude-module",
                "matplotlib",
            ]
        )
    else:
        # Unix-like systems (Linux, macOS)
        cmd.extend(
            [
                "--add-data",
                "python/cocoindex:cocoindex",
                "--exclude-module",
                "tkinter",
                "--exclude-module",
                "matplotlib",
            ]
        )

    print(f"Building executable for {system}...")

    if not run_command(cmd, cwd=project_root):
        print("Build failed!")
        return False

    # Find the generated executable
    executable_name = "cocoindex-watcher"
    if system == "windows":
        executable_name += ".exe"

    executable_path = output_path / executable_name

    if executable_path.exists():
        print(f"✓ Executable built successfully: {executable_path}")
        print(f"  Size: {executable_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print("✗ Executable not found after build")
        return False


def test_executable(output_dir="dist"):
    """Test the built executable."""
    project_root = Path(__file__).parent
    executable_name = "cocoindex-watcher"

    if platform.system().lower() == "windows":
        executable_name += ".exe"

    executable_path = project_root / output_dir / executable_name

    if not executable_path.exists():
        print("Executable not found for testing")
        return False

    print("Testing executable...")

    # Test help command
    cmd = [str(executable_path), "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✓ Executable test passed")
        return True
    else:
        print(f"✗ Executable test failed: {result.stderr}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build CocoIndex Standalone Watcher")
    parser.add_argument(
        "--output-dir", default="dist", help="Output directory for built executable"
    )
    parser.add_argument("--clean", action="store_true", help="Clean previous builds")
    parser.add_argument("--test", action="store_true", help="Test the built executable")
    parser.add_argument(
        "--skip-deps-check", action="store_true", help="Skip dependency checks"
    )

    args = parser.parse_args()

    print("CocoIndex Standalone Watcher Build Script")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print()

    # Check dependencies
    if not args.skip_deps_check:
        if not check_dependencies():
            print("Dependency check failed. Exiting.")
            sys.exit(1)
        print()

    # Build executable
    if not build_executable(args.output_dir, args.clean):
        print("Build failed!")
        sys.exit(1)

    # Test executable
    if args.test:
        if not test_executable(args.output_dir):
            print("Test failed!")
            sys.exit(1)

    print("\nBuild completed successfully!")
    print(f"Executable location: {Path(args.output_dir) / 'cocoindex-watcher'}")
    print("\nUsage example:")
    print(f"  ./{Path(args.output_dir) / 'cocoindex-watcher'} /path/to/watch ./main.py")


if __name__ == "__main__":
    main()
