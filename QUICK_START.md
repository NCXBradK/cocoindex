# 🚀 Quick Start: CocoIndex Standalone Executable

Get up and running with CocoIndex as a standalone executable in under 5 minutes!

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** running (or use the Docker command below)
3. **CocoIndex** installed: `pip install cocoindex[packaging,embeddings]`

## 🏃‍♂️ Quick Setup

### Step 1: Start PostgreSQL (if needed)

```bash
# Quick PostgreSQL setup with Docker
docker run -d \
  --name cocoindex-postgres \
  -p 5432:5432 \
  -e POSTGRES_DB=cocoindex \
  -e POSTGRES_USER=cocoindex \
  -e POSTGRES_PASSWORD=cocoindex \
  ankane/pgvector
```

### Step 2: Build the Standalone Executable

```bash
# Clone or download the CocoIndex project
git clone https://github.com/cocoindex-io/cocoindex.git
cd cocoindex

# Build the executable
python build_executable.py --clean --test
```

### Step 3: Set Up Example Data

```bash
# Create and run the example flow to set up test data
python example_flow.py

# Set up the database schema
cocoindex setup example_flow.py
```

### Step 4: Run the Standalone Watcher

```bash
# Start watching the ./watched_data directory
./dist/cocoindex-watcher ./watched_data ./example_flow.py --initial-index

# On Windows:
# dist\cocoindex-watcher.exe .\watched_data .\example_flow.py --initial-index
```

### Step 5: Test It!

```bash
# In another terminal, add a new file to the watched directory
echo "This is a new document about artificial intelligence and its applications in healthcare." > watched_data/new_document.txt

# Watch the watcher terminal - it should automatically detect and index the new file!
```

## 🎉 You're Done!

The standalone executable is now:
- ✅ Watching `./watched_data` for file changes
- ✅ Automatically indexing new or modified files
- ✅ Storing embeddings in PostgreSQL with vector search
- ✅ Running without Docker dependencies

## 🔧 Customization

### Watch Different Directories

```bash
# Watch your project documents
./dist/cocoindex-watcher /path/to/your/documents ./your_flow.py

# Watch with custom settings
./dist/cocoindex-watcher /path/to/watch ./flow.py --debounce 10 --initial-index
```

### Create Your Own Flow

Copy and modify `example_flow.py`:

```python
@cocoindex.flow_def(name="YourCustomFlow")
def your_custom_flow(flow_builder, data_scope):
    # Your custom indexing logic here
    data_scope["docs"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(path="./your_data")
    )
    # ... rest of your flow
```

## 🚀 Production Usage

### Deploy as a Service

**Linux (systemd):**
```ini
# /etc/systemd/system/cocoindex-watcher.service
[Unit]
Description=CocoIndex File Watcher
After=network.target

[Service]
Type=simple
User=cocoindex
ExecStart=/opt/cocoindex/cocoindex-watcher /data/documents /opt/cocoindex/flow.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Windows (Service):**
```batch
sc create "CocoIndex Watcher" binPath="C:\Tools\cocoindex-watcher.exe C:\Data C:\Config\flow.py"
sc start "CocoIndex Watcher"
```

### Docker-less Deployment

```bash
# Copy executable to target server
scp dist/cocoindex-watcher server:/usr/local/bin/

# Run on server
ssh server "cocoindex-watcher /data/documents /opt/flow.py"
```

## 📊 Performance Tips

1. **Adjust debounce time** for busy directories: `--debounce 30`
2. **Use non-recursive watching** for large directory trees: `--no-recursive`
3. **Monitor memory usage** with `htop` or Task Manager
4. **Use indexed databases** for better query performance

## 🔍 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "CocoIndex is not available" | Ensure `cocoindex --version` works |
| "Permission denied" | `chmod +x cocoindex-watcher` |
| "Database connection failed" | Check PostgreSQL is running |
| "Watch path does not exist" | Verify directory exists and is accessible |

### Debug Mode

```bash
# Enable debug logging
export COCOINDEX_LOG_LEVEL=DEBUG
./dist/cocoindex-watcher ./watched_data ./example_flow.py
```

## 📈 Next Steps

1. **Scale up**: Run multiple watchers for different directories
2. **Integrate**: Add to your existing CI/CD pipeline
3. **Customize**: Build your own indexing flows
4. **Monitor**: Set up logging and alerting
5. **Optimize**: Tune performance for your specific use case

## 📞 Need Help?

- 📖 **Full Documentation**: [STANDALONE_EXECUTABLE.md](STANDALONE_EXECUTABLE.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/cocoindex-io/cocoindex/issues)
- 💬 **Community**: [Discord](https://discord.com/invite/zpA9S2DR7s)
- 🎥 **Video Tutorial**: [YouTube](https://www.youtube.com/@cocoindex-io)

Happy indexing! 🌴 