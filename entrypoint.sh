#!/bin/bash
set -e

MODE=${COCOINDEX_MODE:-watch}

if [ "$MODE" = "server" ]; then
    exec /start_mcp_server.sh
else
    exec python watch_and_index.py
fi 