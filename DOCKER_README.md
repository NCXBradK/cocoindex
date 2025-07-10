# Cocoa Index Docker Setup

This guide explains how to run the Cocoa Index application and all its dependencies in Docker containers using Docker Compose. This setup supports all example workflows and enables both automatic indexing of files in a mounted host folder AND serves as an MCP server for LLM agents simultaneously.

---

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.

---

## 1. Build and Start the Stack

From the project root, run:

```bash
docker compose up --build
```

This will:
- Build the Cocoa Index application container
- Start PostgreSQL, Qdrant, and Neo4j databases
- **Automatically start both**:
  - File watcher that monitors `/data_to_index` for changes
  - MCP server that exposes REST APIs on port 8000

---

## 2. Mount a Host Folder for Indexing

The container automatically watches the `/data_to_index` folder inside the container. To index files from your host system:

1. **Create a folder** on your host (e.g., `./data_to_index`)
2. **Place files** you want to index in this folder
3. **The container will automatically detect changes** and trigger indexing

The `docker-compose.yml` already mounts `./data_to_index` from your host to `/data_to_index` in the container.

---

## 3. How It Works

### Dual Functionality
The Cocoa Index container runs **both services simultaneously**:

1. **File Watcher**: Monitors `/data_to_index` for file changes and triggers indexing
2. **MCP Server**: Exposes REST APIs on port 8000 for LLM agents and other clients

### File Watching
- Uses Python's `watchdog` library to monitor file system events
- Triggers indexing automatically when files are added, modified, or deleted
- Supports recursive monitoring of subdirectories

### MCP Server
- Exposes REST APIs for LLM agents and other clients
- Listens on `http://localhost:8000` by default
- Provides endpoints for querying indexed data and managing flows

---

## 4. Test the Setup

### Test File Indexing
1. Create some test files in the `data_to_index` folder:
   ```bash
   mkdir -p data_to_index
   echo "This is a test document" > data_to_index/test.txt
   ```

2. Watch the container logs to see indexing in action:
   ```bash
   docker compose logs -f coco_app
   ```

### Test the MCP Server
Test the API endpoints:

```bash
curl http://localhost:8000/cocoindex
```

You should see a response like:
```
CocoIndex is running!
```

---

## 5. Running Example Workflows

All examples in the `examples/` directory are supported. To run an example:

```bash
# Enter the container
docker compose exec coco_app bash

# Navigate to an example
cd examples/text_embedding

# Run the example
python main.py
```

---

## 6. Services and Ports

| Service | Port | Purpose |
|---------|------|---------|
| **coco_app** | 8000 | MCP Server API |
| **coco_postgres** | 5432 | PostgreSQL Database |
| **coco_qdrant** | 6333, 6334 | Qdrant Vector Database |
| **coco_neo4j** | 7474, 7687 | Neo4j Graph Database |

---

## 7. Environment Variables

You can customize the behavior using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `COCOINDEX_DATABASE_URL` | `postgresql://postgres:postgres@coco_postgres:5432/cocoindex` | PostgreSQL connection string |
| `QDRANT_URL` | `http://coco_qdrant:6334` | Qdrant connection URL |
| `NEO4J_URI` | `bolt://coco_neo4j:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `neo4j` | Neo4j password |
| `APP_TARGET` | `python/cocoindex/cli.py` | Target app for MCP server |
| `ADDRESS` | `0.0.0.0:8000` | MCP server bind address |

---

## 8. Data Persistence

Database data is persisted using Docker volumes:
- `coco_postgres_data`: PostgreSQL data
- `coco_qdrant_data`: Qdrant vector data  
- `coco_neo4j_data`: Neo4j graph data

To reset all data:
```bash
docker compose down -v
```

---

## 9. Logs and Debugging

View logs for all services:
```bash
docker compose logs -f
```

View logs for a specific service:
```bash
docker compose logs -f coco_app
docker compose logs -f coco_postgres
```

---

## 10. Stopping the Stack

```bash
# Stop all services
docker compose down

# Stop and remove volumes (deletes all data)
docker compose down -v
```

---

## 11. Using with LLM Agents

The MCP server exposes REST APIs that LLM agents can use to:
- Query indexed documents
- Manage data flows
- Trigger indexing operations
- Access vector search capabilities

Example API usage:
```bash
# Get system status
curl http://localhost:8000/cocoindex

# Query indexed documents (example endpoint)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

---

## 12. Troubleshooting

**Container fails to start:**
- Check that all required ports (8000, 5432, 6333, 6334, 7474, 7687) are available
- Ensure Docker has sufficient resources allocated

**File changes not detected:**
- Verify the `data_to_index` folder is properly mounted
- Check container logs for file watcher errors

**Database connection errors:**
- Ensure all database containers are running: `docker compose ps`
- Check database logs: `docker compose logs coco_postgres`

**MCP server not responding:**
- Verify port 8000 is not blocked by firewall
- Check if the server started successfully in container logs 