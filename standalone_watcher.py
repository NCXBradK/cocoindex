#!/usr/bin/env python3
"""
Standalone CocoIndex File Watcher & MCP Server
A self-contained executable that can:
1. Watch directories for changes and trigger CocoIndex indexing
2. Run an MCP server for LLM agents to connect to
3. Run both services simultaneously for complete automation
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import threading
from pathlib import Path
from typing import Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Error: watchdog package is required but not installed.")
    print("Install with: pip install watchdog")
    sys.exit(1)

# Global variables for graceful shutdown
observer = None
mcp_server_process = None
shutdown_event = threading.Event()
mcp_server_thread = None


class CocoIndexEventHandler(FileSystemEventHandler):
    """File system event handler that triggers CocoIndex indexing."""

    def __init__(self, watch_path: str, app_target: str, debounce_seconds: float = 2.0):
        self.watch_path = Path(watch_path)
        self.app_target = app_target
        self.debounce_seconds = debounce_seconds
        self.last_trigger_time = 0
        self.lock = threading.Lock()

    def on_any_event(self, event):
        """Handle any file system event."""
        if event.is_directory:
            return

        # Debounce rapid file changes
        current_time = time.time()
        with self.lock:
            if current_time - self.last_trigger_time < self.debounce_seconds:
                return
            self.last_trigger_time = current_time

        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Change detected: {event.src_path}"
        )
        self.trigger_indexing()

    def trigger_indexing(self):
        """Trigger CocoIndex indexing operation."""
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting indexing...")

            # Check if cocoindex is available
            if not self.check_cocoindex_available():
                print(
                    "Error: CocoIndex is not available. Please ensure it's installed and in PATH."
                )
                return

            # Run the indexing command
            cmd = ["cocoindex", "update", self.app_target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Indexing completed successfully"
                )
                if result.stdout.strip():
                    print(f"Output: {result.stdout.strip()}")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Indexing failed")
                print(f"Error: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⏱️  Indexing timed out after 5 minutes"
            )
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error during indexing: {e}")

    def check_cocoindex_available(self) -> bool:
        """Check if cocoindex command is available."""
        try:
            result = subprocess.run(
                ["cocoindex", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False


def setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        print(
            f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Received signal {signum}, shutting down..."
        )
        shutdown_event.set()

        # Stop the file watcher
        global observer
        if observer:
            observer.stop()

        # Stop the MCP server
        global mcp_server_process
        if mcp_server_process and mcp_server_process.poll() is None:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Terminating MCP server...")
            mcp_server_process.terminate()
            try:
                mcp_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Force killing MCP server..."
                )
                mcp_server_process.kill()

        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)


def validate_paths(watch_path: str, app_target: str) -> tuple[Path, Path]:
    """Validate and resolve paths."""
    watch_path_obj = Path(watch_path).resolve()
    app_target_obj = Path(app_target).resolve()

    if not watch_path_obj.exists():
        raise FileNotFoundError(f"Watch path does not exist: {watch_path_obj}")

    if not watch_path_obj.is_dir():
        raise NotADirectoryError(f"Watch path is not a directory: {watch_path_obj}")

    if not app_target_obj.exists():
        raise FileNotFoundError(f"App target does not exist: {app_target_obj}")

    return watch_path_obj, app_target_obj


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Standalone CocoIndex File Watcher & MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # File watcher only
  %(prog)s /path/to/watch ./main.py
  
  # File watcher with MCP server
  %(prog)s /path/to/watch ./main.py --with-mcp-server --address 0.0.0.0:8000
  
  # MCP server only
  %(prog)s --mcp-server-only --flow-file flows.py
        """,
    )

    parser.add_argument(
        "watch_path",
        nargs="?",
        help="Path to directory to watch for changes (not required for MCP server only mode)",
    )

    parser.add_argument(
        "app_target",
        nargs="?",
        help="Path to CocoIndex application file (e.g., main.py, not required for MCP server only mode)",
    )

    parser.add_argument(
        "--debounce-seconds",
        type=float,
        default=2.0,
        help="Seconds to wait after file changes before triggering indexing (default: 2.0)",
    )

    parser.add_argument(
        "--mcp-server-only",
        action="store_true",
        help="Run as MCP server only (no file watching)",
    )

    parser.add_argument(
        "--with-mcp-server",
        action="store_true",
        help="Run MCP server alongside file watcher",
    )

    parser.add_argument(
        "--address",
        type=str,
        default="0.0.0.0:8000",
        help="Address to bind the MCP server to (default: 0.0.0.0:8000)",
    )

    parser.add_argument(
        "--flow-file",
        type=str,
        default="example_flow.py",
        help="Python file containing CocoIndex flow definitions for MCP server (default: example_flow.py)",
    )

    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't watch subdirectories recursively",
    )

    parser.add_argument(
        "--initial-index",
        action="store_true",
        help="Run initial indexing before starting to watch",
    )

    parser.add_argument(
        "--version", action="version", version="CocoIndex Standalone Watcher v2.0.0"
    )

    return parser.parse_args()


def run_mcp_server(address: str, flow_file: str) -> None:
    """Run CocoIndex as an MCP server."""
    print(f"Starting CocoIndex MCP server on {address}")
    print(f"Using flow file: {flow_file}")

    # Validate that the flow file exists
    if not os.path.exists(flow_file):
        print(f"Error: Flow file '{flow_file}' not found!")
        print("Make sure your flow file is accessible from the current directory.")
        sys.exit(1)

    try:
        # Import cocoindex to ensure it's available
        subprocess.run(
            [sys.executable, "-c", "import cocoindex"], check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print("Error: CocoIndex is not installed or not accessible!")
        sys.exit(1)

    # Run the CocoIndex MCP server
    cmd = [
        sys.executable,
        "-m",
        "cocoindex.cli",
        "server",
        flow_file,
        "--address",
        address,
    ]

    print(f"Executing: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running MCP server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMCP server stopped by user.")
        sys.exit(0)


def run_mcp_server_threaded(address: str, flow_file: str) -> None:
    """Run CocoIndex MCP server in a separate thread."""
    global mcp_server_process

    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting CocoIndex MCP server on {address}"
    )
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Using flow file: {flow_file}")

    # Validate that the flow file exists
    if not os.path.exists(flow_file):
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Flow file '{flow_file}' not found!"
        )
        print("Make sure your flow file is accessible from the current directory.")
        return

    try:
        # Import cocoindex to ensure it's available
        subprocess.run(
            [sys.executable, "-c", "import cocoindex"], check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: CocoIndex is not installed or not accessible!"
        )
        return

    # Run the CocoIndex MCP server as a subprocess
    cmd = [
        sys.executable,
        "-m",
        "cocoindex.cli",
        "server",
        flow_file,
        "--address",
        address,
    ]

    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting MCP server with command: {' '.join(cmd)}"
    )

    try:
        mcp_server_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Wait for the process to complete or be terminated
        while not shutdown_event.is_set():
            if mcp_server_process.poll() is not None:
                # Process has terminated
                stdout, stderr = mcp_server_process.communicate()
                if stdout:
                    print(
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] MCP Server stdout: {stdout}"
                    )
                if stderr:
                    print(
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] MCP Server stderr: {stderr}"
                    )
                break
            time.sleep(0.1)

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error running MCP server: {e}")
    finally:
        if mcp_server_process and mcp_server_process.poll() is None:
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Terminating MCP server process..."
            )
            mcp_server_process.terminate()
            try:
                mcp_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Force killing MCP server process..."
                )
                mcp_server_process.kill()


def main() -> None:
    """Main entry point for the standalone watcher."""
    global mcp_server_thread

    args = parse_arguments()

    # If MCP server only mode is requested, run the MCP server only
    if args.mcp_server_only:
        run_mcp_server(args.address, args.flow_file)
        return

    # Validate arguments for file watcher mode
    if not args.watch_path or not args.app_target:
        print(
            "Error: watch_path and app_target are required unless using --mcp-server-only"
        )
        sys.exit(1)

    # Validate arguments
    try:
        watch_path, app_target = validate_paths(args.watch_path, args.app_target)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Setup signal handlers
    setup_signal_handlers()

    # Start MCP server in a separate thread if requested
    if args.with_mcp_server:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting MCP server thread...")
        mcp_server_thread = threading.Thread(
            target=run_mcp_server_threaded,
            args=(args.address, args.flow_file),
            daemon=True,
        )
        mcp_server_thread.start()
        time.sleep(2)  # Give the MCP server a moment to start

    # Create event handler for file watching
    event_handler = CocoIndexEventHandler(
        str(watch_path), str(app_target), args.debounce_seconds
    )

    # Check if CocoIndex is available
    if not event_handler.check_cocoindex_available():
        print(
            "Error: CocoIndex is not available. Please ensure it's installed and in PATH."
        )
        sys.exit(1)

    # Run initial indexing if requested
    if args.initial_index:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running initial indexing...")
        event_handler.trigger_indexing()

    # Start watching
    mode_desc = "File Watcher"
    if args.with_mcp_server:
        mode_desc += " + MCP Server"

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting CocoIndex {mode_desc}")
    print(f"  Watch Path: {watch_path}")
    print(f"  App Target: {app_target}")
    print(f"  Recursive: {not args.no_recursive}")
    print(f"  Debounce: {args.debounce_seconds}s")

    if args.with_mcp_server:
        print(f"  MCP Server: {args.address}")
        print(f"  Flow File: {args.flow_file}")

    print(f"  Press Ctrl+C to stop")

    global observer
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=not args.no_recursive)

    try:
        observer.start()

        # Keep the main thread alive
        while not shutdown_event.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Keyboard interrupt received")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error: {e}")
    finally:
        # Cleanup
        shutdown_event.set()

        if observer:
            observer.stop()
            observer.join()

        if mcp_server_thread and mcp_server_thread.is_alive():
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Waiting for MCP server thread to finish..."
            )
            mcp_server_thread.join(timeout=5)

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Services stopped")


if __name__ == "__main__":
    main()
