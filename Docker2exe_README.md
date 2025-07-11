# CocoIndex Docker2exe - Standalone Executable (Alternative Approach)

> **🚀 New Option Available!** We now offer **dockerc** as a faster alternative to Docker2exe. See `./build_dockerc.sh` for the recommended approach.

Convert your CocoIndex application into a truly standalone executable that includes both the database and indexing capabilities.

## 🎯 What is This?

This solution uses **Docker2exe** to package CocoIndex + PostgreSQL into a single executable file. Unlike traditional approaches, this creates a **truly self-contained application** that doesn't require external database setup.

## 🔄 Two Available Approaches

### **Option 1: dockerc (Recommended)**
- ⚡ **Faster builds** (~5-10 minutes vs 15-30 minutes)
- 📦 **Smaller executables** (~200-300MB vs 300-500MB)
- 🚀 **Better performance** (faster startup, less memory)
- 🔧 **Modern tooling** (actively maintained)

```bash
./build_dockerc.sh
```

### **Option 2: Docker2exe (This approach)**
- 🏛️ **More mature** (established, stable)
- 📚 **Well-documented** (lots of examples)
- 🔄 **Embedded mode** (packs entire Docker image)
- 🌐 **Wider compatibility** (works on more systems)

```bash
./build_monolith.sh
```

## 🚀 Quick Start (Docker2exe)

### 1. Build the Executable

```bash
# Clone the repository
git clone https://github.com/yourorg/cocoindex.git
cd cocoindex

# Build the standalone executable (one command!)
./build_monolith.sh
```

### 2. Use the Executable

```bash
# Start watching a directory
./dist/cocoindex-watcher-linux-amd64 --watch-path /path/to/documents

# Windows
.\dist\cocoindex-watcher-windows-amd64.exe --watch-path C:\Documents

# macOS
./dist/cocoindex-watcher-darwin-amd64 --watch-path /Users/username/Documents
```

## 📊 Performance Comparison

| Feature | dockerc | Docker2exe |
|---------|---------|------------|
| Build Time | ~5-10 min | ~15-30 min |
| Executable Size | ~200-300MB | ~300-500MB |
| Startup Time | ~2-3 sec | ~5-10 sec |
| Memory Usage | ~100-200MB | ~200-400MB |
| CPU Usage | Lower | Higher |

## 💡 When to Use Docker2exe

Choose Docker2exe when:
- ✅ **Maximum compatibility** is needed
- ✅ **Established tooling** is preferred
- ✅ **Infrequent builds** (build time less important)
- ✅ **dockerc doesn't work** for your specific use case
- ✅ **Embedded mode** is specifically required

## 🔧 Build Process Details

### What the Build Script Does

1. **Dependencies Check** - Verifies Docker is installed
2. **Docker2exe Download** - Gets the latest Docker2exe binary
3. **Docker Image Build** - Creates monolithic container
4. **Executable Creation** - Converts image to standalone binary
5. **Testing & Packaging** - Verifies executable works

### Build Options

```bash
# Build with embedded mode (larger but truly standalone)
./build_monolith.sh --embed

# Build without embedding (smaller, requires Docker pull)
./build_monolith.sh --no-embed

# Build for specific platform
./build_monolith.sh --platform linux
```

## 📁 File Structure After Build

```
cocoindex/
├── dist/
│   ├── cocoindex-watcher-linux-amd64
│   ├── cocoindex-watcher-darwin-amd64
│   └── cocoindex-watcher-windows-amd64.exe
├── docker2exe (downloaded tool)
└── build_monolith.sh (build script)
```

## 🌟 Benefits Over Traditional Docker

### Before (Docker Compose)
```yaml
# Complex setup needed in every project
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: cocoindex
      POSTGRES_USER: cocoindex
      POSTGRES_PASSWORD: cocoindex
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  cocoindex:
    image: cocoindex:latest
    depends_on:
      - postgres
    environment:
      COCOINDEX_DATABASE_URL: postgres://cocoindex:cocoindex@postgres/cocoindex
    volumes:
      - ./watch-data:/data
```

### After (Docker2exe Executable)
```bash
# Single command - no configuration needed!
./cocoindex-watcher --watch-path ./watch-data
```

## 🐛 Troubleshooting

### Common Issues

**Build fails with "Docker2exe not found"**
```bash
# Manual download
curl -L https://github.com/rzane/docker2exe/releases/latest/download/docker2exe-linux-amd64 -o docker2exe
chmod +x docker2exe
```

**Executable fails to start**
```bash
# Check permissions
chmod +x ./dist/cocoindex-watcher-linux-amd64

# Test with minimal args
./dist/cocoindex-watcher-linux-amd64 --help
```

**Large executable size**
```bash
# Try without embedding for smaller size
./build_monolith.sh --no-embed
```

## 📈 Distribution & Deployment

### Single File Distribution
```bash
# Copy executable to target system
scp dist/cocoindex-watcher-linux-amd64 user@server:/usr/local/bin/

# Make it executable
chmod +x /usr/local/bin/cocoindex-watcher-linux-amd64
```

### Integration Examples
```bash
# Watch documents folder
./cocoindex-watcher --watch-path /home/user/documents

# Watch with custom patterns
./cocoindex-watcher --watch-path /docs --patterns "*.md,*.txt,*.pdf"

# Background process
nohup ./cocoindex-watcher --watch-path /data &
```

## 🎯 Migration from dockerc

If you're switching from dockerc to Docker2exe:

1. **Same Docker image** - Both use `Dockerfile.monolith`
2. **Same usage** - Executable interface is identical
3. **Different build** - Just use `./build_monolith.sh` instead
4. **Larger file** - Expect 100-200MB larger executables

## 🔄 Alternative: Try dockerc First

Before using Docker2exe, consider trying the faster dockerc approach:

```bash
# Try dockerc first (recommended)
./build_dockerc.sh

# Fall back to Docker2exe if needed
./build_monolith.sh
```

## 📞 Support

- **Documentation**: See `STANDALONE_EXECUTABLE.md` for comprehensive guide
- **Issues**: Report at [GitHub Issues](https://github.com/cocoindex-io/cocoindex/issues)
- **Docker2exe**: Visit [Docker2exe GitHub](https://github.com/rzane/docker2exe)

## 🎉 Success!

You now have a standalone CocoIndex executable that includes everything needed to run without any external dependencies. While dockerc is typically faster to build, Docker2exe offers proven reliability and maximum compatibility.

**Happy indexing! 🚀** 