# CocoIndex Standalone Executable

This guide explains how to package CocoIndex as a standalone executable using two different approaches, creating a truly self-contained application that includes both the database and indexing capabilities.

## 🎯 Overview

Both approaches provide:
- **Truly standalone** - Includes PostgreSQL database + CocoIndex in one executable
- **Self-contained** - No external dependencies (except Docker runtime for build)
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Easy distribution** - Single executable file deployment
- **No setup required** - Database and application bundled together

## 🚀 Two Build Approaches

### **Option 1: dockerc (Recommended - Faster)**

[dockerc](https://github.com/NilsIrl/dockerc) is a modern "container image to single executable compiler" that's typically faster and more efficient than Docker2exe.

**Advantages:**
- ⚡ **Faster build times** - More efficient conversion process
- 🚀 **Better performance** - Optimized runtime with rootless containers
- 💾 **Smaller executables** - Better compression and optimization
- 🔧 **Active development** - Modern, well-maintained project

**Build Command:**
```bash
# One-command build
./build_dockerc.sh
```

### **Option 2: Docker2exe (Alternative)**

Traditional Docker-to-executable conversion tool that's more established but slower.

**Advantages:**
- 🏛️ **Mature and stable** - Long-established tool
- 📚 **Well-documented** - Lots of examples and community support
- 🔄 **Embedded mode** - Packs entire Docker image into executable

**Build Command:**
```bash
# One-command build
./build_monolith.sh
```

## 📋 Prerequisites

1. **Docker installed** on build machine
2. **Git** and **curl** for downloading tools
3. **Build tools** (automatically installed by scripts)

## 🏃‍♂️ Quick Start

### 1. Choose Your Build Method

```bash
# Clone the repository
git clone https://github.com/yourorg/cocoindex.git
cd cocoindex

# Option A: dockerc (recommended)
./build_dockerc.sh

# Option B: Docker2exe (alternative)
./build_monolith.sh
```

### 2. Use the Executable

```bash
# The executable will be in the dist/ directory
ls -la dist/

# Example usage
./dist/cocoindex-watcher-linux-x86_64 --watch-path /path/to/documents

# Windows
./dist/cocoindex-watcher-windows-x86_64.exe --watch-path C:\Documents
```

## 🔧 Build Process Details

### What Both Scripts Do:

1. **Check Dependencies** - Verify Docker is installed
2. **Download Tools** - Get dockerc or Docker2exe automatically
3. **Build Docker Image** - Create monolithic container with PostgreSQL + CocoIndex
4. **Convert to Executable** - Transform Docker image into standalone binary
5. **Test & Package** - Verify executable works and provide usage examples

### Build Time Comparison:

| Tool | Typical Build Time | Executable Size | Performance |
|------|-------------------|-----------------|-------------|
| dockerc | ~5-10 minutes | ~200-300MB | Faster startup |
| Docker2exe | ~15-30 minutes | ~300-500MB | Slower startup |

## 💡 Usage Examples

### Basic File Watching
```bash
# Watch a directory and index all files
./cocoindex-watcher --watch-path /home/user/documents

# Watch specific file types
./cocoindex-watcher --watch-path /docs --patterns "*.md,*.txt,*.pdf"
```

### Advanced Configuration
```bash
# Use custom CocoIndex flow
./cocoindex-watcher --watch-path /data --flow-file ./my_flow.py

# Configure database settings
./cocoindex-watcher --watch-path /docs --db-url "postgres://user:pass@localhost/mydb"

# Set logging level
./cocoindex-watcher --watch-path /docs --log-level DEBUG
```

## 🏗️ Distribution

### Single File Distribution
```bash
# Copy executable to target system
scp dist/cocoindex-watcher-linux-x86_64 user@server:/usr/local/bin/

# Make it executable
chmod +x /usr/local/bin/cocoindex-watcher-linux-x86_64

# Run anywhere
/usr/local/bin/cocoindex-watcher-linux-x86_64 --watch-path /var/data
```

### Integration with Other Projects
```bash
# No Docker Compose needed!
# Just add executable to your project
./cocoindex-watcher --watch-path ./my-project-data &

# Or integrate into existing scripts
./deploy.sh && ./cocoindex-watcher --watch-path ./generated-docs
```

## 🐛 Troubleshooting

### Build Issues
```bash
# Clean Docker cache if builds fail
docker system prune -a

# Check Docker is running
docker ps

# Rebuild with verbose output
docker build -f Dockerfile.monolith -t cocoindex-monolith --progress=plain .
```

### Runtime Issues
```bash
# Check executable permissions
chmod +x ./dist/cocoindex-watcher-*

# Test with minimal args
./dist/cocoindex-watcher-linux-x86_64 --help

# Run with debug logging
./dist/cocoindex-watcher-linux-x86_64 --watch-path /tmp --log-level DEBUG
```

## 🎯 When to Use Each Approach

### Use **dockerc** when:
- ✅ You want faster build times
- ✅ You need smaller executables
- ✅ You're building regularly (development/CI)
- ✅ You want modern tooling

### Use **Docker2exe** when:
- ✅ You need maximum compatibility
- ✅ You're building infrequently
- ✅ You prefer established tools
- ✅ dockerc doesn't work for your use case

## 📈 Performance Comparison

| Metric | dockerc | Docker2exe |
|--------|---------|------------|
| Build Speed | 🚀 Fast | 🐌 Slow |
| Executable Size | 📦 Smaller | 📦 Larger |
| Runtime Performance | ⚡ Faster | ⚡ Moderate |
| Memory Usage | 💾 Efficient | 💾 Higher |
| Startup Time | 🏃 Quick | 🏃 Slower |

## 🌟 Benefits Over Traditional Deployment

### Before (Docker Compose):
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

### After (Standalone Executable):
```bash
# Single command - no configuration needed!
./cocoindex-watcher --watch-path ./watch-data
```

## 🎉 Success!

You now have two powerful options for creating standalone CocoIndex executables that can be distributed and used without any Docker or database setup requirements. Choose the approach that best fits your needs and build requirements!

**Happy indexing! 🚀** 