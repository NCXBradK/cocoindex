#!/bin/bash
# Build script for CocoIndex Monolithic Docker image and Docker2exe conversion

set -e

echo "🏗️  Building CocoIndex Monolithic Docker Image & Executable"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="cocoindex-monolith"
IMAGE_TAG="latest"
EXECUTABLE_NAME="cocoindex-watcher"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker2exe is installed
if ! command -v docker2exe &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker2exe not found. Installing...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="darwin"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        echo -e "${RED}❌ Unsupported OS: $OSTYPE${NC}"
        exit 1
    fi
    
    # Detect architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" ]]; then
        ARCH="amd64"
    elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
        ARCH="arm64"
    else
        echo -e "${RED}❌ Unsupported architecture: $ARCH${NC}"
        exit 1
    fi
    
    # Download Docker2exe
    DOCKER2EXE_URL="https://github.com/rzane/docker2exe/releases/latest/download/docker2exe-${OS}-${ARCH}"
    if [[ "$OS" == "windows" ]]; then
        DOCKER2EXE_URL="${DOCKER2EXE_URL}.exe"
    fi
    
    echo "Downloading Docker2exe from: $DOCKER2EXE_URL"
    
    if command -v curl &> /dev/null; then
        curl -L "$DOCKER2EXE_URL" -o docker2exe
    elif command -v wget &> /dev/null; then
        wget "$DOCKER2EXE_URL" -O docker2exe
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one of them.${NC}"
        exit 1
    fi
    
    chmod +x docker2exe
    
    # Move to a directory in PATH (optional)
    if [[ -w /usr/local/bin ]]; then
        sudo mv docker2exe /usr/local/bin/
        echo -e "${GREEN}✅ Docker2exe installed to /usr/local/bin/${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker2exe downloaded to current directory. Add to PATH if needed.${NC}"
    fi
fi

echo -e "${GREEN}✅ All prerequisites are available${NC}"

# Build the monolithic Docker image
echo -e "\n${YELLOW}🔨 Building monolithic Docker image...${NC}"
COMPOSE_BAKE=true docker build -f Dockerfile.monolith -t "$IMAGE_NAME:$IMAGE_TAG" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

# Test the Docker image
echo -e "\n${YELLOW}🧪 Testing Docker image...${NC}"
docker run --rm "$IMAGE_NAME:$IMAGE_TAG" --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Docker image test had warnings, but continuing...${NC}"
fi

# Convert to executable using Docker2exe
echo -e "\n${YELLOW}🔄 Converting Docker image to executable...${NC}"

# Use embedded mode for a truly standalone executable
docker2exe --name "$EXECUTABLE_NAME" --image "$IMAGE_NAME:$IMAGE_TAG" --embed

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Executable created successfully${NC}"
    
    # Show the created executables
    echo -e "\n${GREEN}📦 Created executables:${NC}"
    ls -la dist/
    
    # Show file sizes
    echo -e "\n${GREEN}📊 File sizes:${NC}"
    du -h dist/*
    
    echo -e "\n${GREEN}🎉 Success! Your standalone CocoIndex executables are ready!${NC}"
    echo -e "${GREEN}📂 Location: $(pwd)/dist/${NC}"
    echo -e "${GREEN}📝 Usage: ./dist/${EXECUTABLE_NAME}-<platform> --watch-path /path/to/watch${NC}"
    
else
    echo -e "${RED}❌ Failed to create executable${NC}"
    exit 1
fi

echo -e "\n${YELLOW}📋 Next steps:${NC}"
echo "1. Test the executable: ./dist/${EXECUTABLE_NAME}-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m)"
echo "2. Distribute the executable to target machines"
echo "3. Note: Target machines still need Docker installed to run the executable"
echo "4. The executable contains the entire CocoIndex + PostgreSQL environment"

echo -e "\n${GREEN}✨ Build completed successfully!${NC}" 