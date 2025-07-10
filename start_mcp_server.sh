#!/bin/bash
set -e

# Default app target (can be overridden by env or arg)
APP_TARGET=${APP_TARGET:-python/cocoindex/cli.py}
ADDRESS=${ADDRESS:-0.0.0.0:8000}

# Optionally run setup/update for all flows (customize as needed)
# echo yes | cocoindex setup $APP_TARGET
# echo yes | cocoindex update $APP_TARGET

# Start the MCP server
exec python -m cocoindex.cli server $APP_TARGET --address $ADDRESS 