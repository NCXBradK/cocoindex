# CocoIndex MCP Server - Integration Guide

This guide explains how to use the CocoIndex standalone executable as an MCP (Model Context Protocol) server that LLM agents can connect to for document indexing and search capabilities.

## 🎯 What is MCP Server Mode?

The CocoIndex standalone executable can run in **three modes**:

1. **File Watcher Mode** (default) - Watches directories for changes and indexes files
2. **MCP Server Mode** - Runs as an MCP server that LLM agents can connect to
3. **🚀 Hybrid Mode** - Runs **both** file watcher and MCP server simultaneously

## 🌟 **Hybrid Mode (Recommended)**

The hybrid mode is the most powerful option - it automatically indexes files as they change while also providing an MCP server endpoint for LLM agents to query the indexed data.

### Benefits of Hybrid Mode:
- **Automatic indexing** - Files are indexed as soon as they change
- **Real-time search** - LLM agents can query the most up-to-date indexed data
- **Complete automation** - No manual intervention required
- **Single process** - Everything runs in one executable

## 🚀 Quick Start

### 1. Build the Standalone Executable

```bash
# Using dockerc (recommended - faster)
./build_dockerc.sh

# Or using Docker2exe (alternative)
./build_monolith.sh
```

### 2. Run in Hybrid Mode (File Watcher + MCP Server)

```bash
# Start both file watcher and MCP server
./dist/cocoindex-watcher-linux-amd64 /path/to/documents example_flow.py --with-mcp-server --address 0.0.0.0:8000

# Windows
.\dist\cocoindex-watcher-windows-amd64.exe C:\Documents example_flow.py --with-mcp-server --address 0.0.0.0:8000

# macOS
./dist/cocoindex-watcher-darwin-amd64 /Users/yourname/Documents example_flow.py --with-mcp-server --address 0.0.0.0:8000
```

### 3. Alternative: MCP Server Only Mode

```bash
# MCP server only (no file watching)
./dist/cocoindex-watcher-linux-amd64 --mcp-server-only --address 0.0.0.0:8000 --flow-file example_flow.py
```

### 4. Alternative: File Watcher Only Mode

```bash
# File watcher only (no MCP server)
./dist/cocoindex-watcher-linux-amd64 /path/to/documents example_flow.py
```

## 🔧 Configuration for LLM Agents

### Claude Desktop (Recommended for Hybrid Mode)

Create or update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cocoindex": {
      "command": "cocoindex-watcher-linux-amd64",
      "args": [
        "/path/to/your/documents",
        "example_flow.py",
        "--with-mcp-server",
        "--address",
        "0.0.0.0:8000",
        "--flow-file",
        "example_flow.py"
      ],
      "env": {
        "COCOINDEX_DATABASE_URL": "postgres://cocoindex:cocoindex@localhost:5432/cocoindex"
      }
    }
  }
}
```

### MCP Server Only Configuration

If you prefer to run the MCP server separately from file watching:

```json
{
  "mcpServers": {
    "cocoindex-mcp-only": {
      "command": "cocoindex-watcher-linux-amd64",
      "args": [
        "--mcp-server-only",
        "--address",
        "0.0.0.0:8000",
        "--flow-file",
        "example_flow.py"
      ],
      "env": {
        "COCOINDEX_DATABASE_URL": "postgres://cocoindex:cocoindex@localhost:5432/cocoindex"
      }
    }
  }
}
```

## 📋 Command Line Options

### Hybrid Mode Options
```bash
./cocoindex-watcher /path/to/watch flow.py --with-mcp-server [OPTIONS]
```

### MCP Server Only Options
```bash
./cocoindex-watcher --mcp-server-only [OPTIONS]
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--address` | MCP server bind address | `0.0.0.0:8000` |
| `--flow-file` | CocoIndex flow definition file | `example_flow.py` |
| `--debounce-seconds` | Wait time after file changes | `2.0` |
| `--no-recursive` | Don't watch subdirectories | `false` |
| `--initial-index` | Run initial indexing on startup | `false` |

## 🔍 Usage Examples

### Complete Setup Example

```bash
# 1. Start the executable in hybrid mode
./cocoindex-watcher /data/documents flow.py --with-mcp-server --initial-index

# 2. The executable will:
#    - Start the MCP server on port 8000
#    - Watch /data/documents for changes
#    - Run initial indexing of existing files
#    - Automatically index new/changed files
#    - Provide MCP API for LLM agents

# 3. LLM agents can now:
#    - Query indexed documents
#    - Search for specific content
#    - Access metadata and embeddings
```

### Development and Testing

```bash
# Test MCP server connectivity
curl -X POST http://localhost:8000/health

# View logs in real-time
./cocoindex-watcher /data/docs flow.py --with-mcp-server --verbose

# Test with specific flow file
./cocoindex-watcher /data/docs my_custom_flow.py --with-mcp-server --flow-file my_custom_flow.py
```

## 🎯 What LLM Agents Can Do

When connected to the CocoIndex MCP server, LLM agents can:

1. **Search Documents** - Find relevant documents by content
2. **Query Metadata** - Access file information and properties
3. **Semantic Search** - Find conceptually similar content
4. **Data Extraction** - Extract structured data from documents
5. **Real-time Access** - Query the most recently indexed content

## 🛠️ Troubleshooting

### Common Issues

1. **MCP Server won't start**
   - Check if port 8000 is available
   - Verify flow file exists and is valid
   - Ensure database connection works

2. **File watching not working**
   - Check directory permissions
   - Verify path exists and is accessible
   - Test with `--initial-index` flag

3. **Database connection failed**
   - Verify PostgreSQL is running
   - Check COCOINDEX_DATABASE_URL environment variable
   - Ensure database exists and is accessible

### Debug Mode

```bash
# Enable verbose logging
./cocoindex-watcher /path/to/docs flow.py --with-mcp-server --verbose

# Test individual components
./cocoindex-watcher --mcp-server-only --flow-file flow.py  # Test MCP server only
./cocoindex-watcher /path/to/docs flow.py                 # Test file watcher only
```

## 🚀 Next Steps

1. **Create your flow file** - Define how documents should be processed
2. **Configure your LLM agent** - Add the MCP server configuration
3. **Test the integration** - Verify both services work together
4. **Monitor performance** - Check logs and resource usage

For more information, see the main [CocoIndex documentation](README.md). 