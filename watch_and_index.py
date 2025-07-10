import time
import subprocess
import threading
import os
import signal
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_PATH = "/data_to_index"
APP_TARGET = os.environ.get("APP_TARGET", "python/cocoindex/cli.py")
MCP_ADDRESS = os.environ.get("ADDRESS", "0.0.0.0:8000")


class IndexingEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        print(f"Change detected: {event.src_path}. Triggering indexing...")
        # Replace the following with the actual indexing command or function
        try:
            # Example: call the CLI to index the folder
            subprocess.run(
                ["python", "-m", "cocoindex.cli", "index", WATCH_PATH], check=True
            )
            print("Indexing completed successfully.")
        except Exception as e:
            print(f"Error during indexing: {e}")


def start_mcp_server():
    """Start the MCP server in a separate thread"""
    try:
        print(f"Starting MCP server on {MCP_ADDRESS}...")
        # Start the MCP server
        subprocess.run(
            [
                "python",
                "-m",
                "cocoindex.cli",
                "server",
                APP_TARGET,
                "--address",
                MCP_ADDRESS,
            ],
            check=True,
        )
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        # If MCP server fails, we should exit the whole process
        os._exit(1)


def start_file_watcher():
    """Start the file watcher"""
    try:
        print(f"Starting file watcher for {WATCH_PATH}...")

        # Create the watch directory if it doesn't exist
        if not os.path.exists(WATCH_PATH):
            print(f"Creating watch directory: {WATCH_PATH}")
            os.makedirs(WATCH_PATH, exist_ok=True)

        # Set up file watcher
        event_handler = IndexingEventHandler()
        observer = Observer()
        observer.schedule(event_handler, WATCH_PATH, recursive=True)
        observer.start()

        print(f"File watcher started. Monitoring {WATCH_PATH} for changes...")

        # Keep the watcher running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping file watcher...")
            observer.stop()
        observer.join()

    except Exception as e:
        print(f"Error in file watcher: {e}")
        os._exit(1)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"Received signal {signum}. Shutting down...")
    sys.exit(0)


def main():
    """Main function that starts both services"""
    print("Starting Cocoa Index with both file watcher and MCP server...")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start MCP server in a background thread
    mcp_thread = threading.Thread(target=start_mcp_server, daemon=True)
    mcp_thread.start()

    # Give the MCP server a moment to start
    time.sleep(2)
    print("MCP server started in background thread.")

    # Start file watcher in the main thread
    start_file_watcher()


if __name__ == "__main__":
    main()
