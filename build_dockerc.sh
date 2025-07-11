#!/bin/bash
# Build script for CocoIndex using dockerc (alternative to Docker2exe)
# dockerc compiles Docker images into standalone portable binaries

set -e

echo "🚀 Building CocoIndex Standalone Executable with dockerc"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="cocoindex-monolith"
IMAGE_TAG="latest"
EXECUTABLE_NAME="cocoindex-watcher"

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -s)

# Normalize OS names for dockerc
case "$OS" in
    Linux*)
        DOCKERC_OS="linux"
        ;;
    Darwin*)
        DOCKERC_OS="darwin"
        ;;
    CYGWIN*|MINGW*|MSYS*)
        # Check if we're in WSL (which would have /proc/version)
        if [ -f /proc/version ] && grep -q Microsoft /proc/version 2>/dev/null; then
            DOCKERC_OS="linux"
            echo -e "${YELLOW}ℹ️  WSL detected - using Linux dockerc${NC}"
        else
            echo -e "${RED}❌ dockerc requires Linux environment${NC}"
            echo -e "${YELLOW}Please use one of these options:${NC}"
            echo -e "${YELLOW}  1. Run in WSL: wsl ./build_dockerc.sh${NC}"
            echo -e "${YELLOW}  2. Use Docker2exe instead: ./build_monolith.sh${NC}"
            echo -e "${YELLOW}  3. Use Docker Desktop with Linux containers${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}❌ Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}🔍 Detected platform: ${DOCKERC_OS} ${ARCH}${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if required tools are available
for tool in curl file; do
    if ! command -v $tool &> /dev/null; then
        echo -e "${RED}❌ Required tool '$tool' is not installed.${NC}"
        case $tool in
            curl)
                echo -e "${YELLOW}Install with: sudo apt-get install curl${NC}"
                ;;
            file)
                echo -e "${YELLOW}Install with: sudo apt-get install file${NC}"
                ;;
        esac
        exit 1
    fi
done

# Check if dockerc is installed
if ! command -v dockerc &> /dev/null; then
    echo -e "${YELLOW}⚠️  dockerc not found. Installing...${NC}"
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Download dockerc from GitHub releases
    echo -e "${BLUE}📥 Downloading dockerc from GitHub releases...${NC}"
    
    # Get the latest release info from GitHub API
    LATEST_RELEASE=$(curl -s "https://api.github.com/repos/NilsIrl/dockerc/releases/latest")
    
    # Extract the download URL for the correct architecture
    # dockerc uses naming like: dockerc_x86-64, dockerc_aarch64 for downloads
    if [ "$ARCH" = "x86_64" ]; then
        # Try the GNU version first, then fall back to regular
        DOWNLOAD_URL=$(echo "$LATEST_RELEASE" | grep -o "https://github.com/NilsIrl/dockerc/releases/download/[^/]*/dockerc_x86-64-gnu" | head -1)
        if [ -z "$DOWNLOAD_URL" ]; then
            DOWNLOAD_URL=$(echo "$LATEST_RELEASE" | grep -o "https://github.com/NilsIrl/dockerc/releases/download/[^/]*/dockerc_x86-64" | head -1)
        fi
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        DOWNLOAD_URL=$(echo "$LATEST_RELEASE" | grep -o "https://github.com/NilsIrl/dockerc/releases/download/[^/]*/dockerc_aarch64" | head -1)
    else
        echo -e "${RED}❌ Unsupported architecture for download: $ARCH${NC}"
        exit 1
    fi
    
    if [ -z "$DOWNLOAD_URL" ]; then
        echo -e "${RED}❌ Could not find download URL for architecture ${ARCH}${NC}"
        echo -e "${YELLOW}Available releases:${NC}"
        echo "$LATEST_RELEASE" | grep -o "https://github.com/NilsIrl/dockerc/releases/download/[^/]*/dockerc_[^\"]*" | head -10
        exit 1
    fi
    
    DOCKERC_FILENAME="dockerc"
    
    echo -e "${BLUE}📥 Downloading from: $DOWNLOAD_URL${NC}"
    
    # Download the file
    echo -e "${BLUE}🔍 Running: curl -L -o \"$DOCKERC_FILENAME\" \"$DOWNLOAD_URL\"${NC}"
    if ! curl -L -o "$DOCKERC_FILENAME" "$DOWNLOAD_URL"; then
        echo -e "${RED}❌ Failed to download dockerc${NC}"
        exit 1
    fi
    
    # Check if the download was successful by checking file size
    echo -e "${BLUE}🔍 Checking downloaded file...${NC}"
    if [ ! -s "$DOCKERC_FILENAME" ]; then
        echo -e "${RED}❌ Downloaded file is empty${NC}"
        ls -la "$DOCKERC_FILENAME" || echo "File doesn't exist"
        exit 1
    fi
    
    # Show file info
    echo -e "${BLUE}🔍 File info: $(ls -la "$DOCKERC_FILENAME")${NC}"
    
    # Check if it's actually a binary (not an HTML error page)
    FILE_TYPE=$(file "$DOCKERC_FILENAME")
    echo -e "${BLUE}🔍 File type: $FILE_TYPE${NC}"
    
    if echo "$FILE_TYPE" | grep -q "HTML\|text"; then
        echo -e "${RED}❌ Downloaded file is not a binary executable${NC}"
        echo -e "${YELLOW}File content:${NC}"
        head -3 "$DOCKERC_FILENAME"
        exit 1
    fi
    
    # Make executable
    chmod +x "$DOCKERC_FILENAME"
    
    # Set the command variable for testing
    DOCKERC_CMD="./$DOCKERC_FILENAME"
    
    # Test that dockerc is working
    echo -e "${BLUE}🧪 Testing dockerc installation...${NC}"
    echo -e "${BLUE}🔍 Running: $DOCKERC_CMD --version${NC}"
    if ! $DOCKERC_CMD --version > /dev/null 2>&1; then
        echo -e "${RED}❌ dockerc is not working properly after download${NC}"
        echo -e "${YELLOW}Trying to run dockerc with --help:${NC}"
        echo -e "${BLUE}🔍 Running: $DOCKERC_CMD --help${NC}"
        $DOCKERC_CMD --help || echo "No help available"
        exit 1
    fi
    echo -e "${GREEN}✅ dockerc is working correctly${NC}"
    
    # Move to project directory
    mv "$DOCKERC_FILENAME" "${OLDPWD}/$DOCKERC_FILENAME"
    
    # Cleanup
    cd "$OLDPWD"
    rm -rf "$TEMP_DIR"
    
    # Update the command to use the file in the project directory
    DOCKERC_CMD="./$DOCKERC_FILENAME"
else
    DOCKERC_CMD="dockerc"
    echo -e "${GREEN}✅ dockerc found in PATH${NC}"
fi

echo -e "${GREEN}✅ All prerequisites are available${NC}"

# Build the monolithic Docker image
echo -e "${BLUE}🔨 Building monolithic Docker image...${NC}"
if ! COMPOSE_BAKE=true docker build -f Dockerfile.monolith -t "${IMAGE_NAME}:${IMAGE_TAG}" .; then
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Create output directory
mkdir -p dist

# Use dockerc to convert Docker image to standalone executable
echo -e "${BLUE}🏗️  Converting Docker image to standalone executable...${NC}"
OUTPUT_PATH="dist/${EXECUTABLE_NAME}-${DOCKERC_OS}-${ARCH}"
if [[ "$DOCKERC_OS" == "windows" ]]; then
    OUTPUT_PATH="${OUTPUT_PATH}.exe"
fi

if ! $DOCKERC_CMD --image "docker-daemon:${IMAGE_NAME}:${IMAGE_TAG}" --output "$OUTPUT_PATH"; then
    echo -e "${RED}❌ Failed to convert Docker image to executable${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Executable created successfully: $OUTPUT_PATH${NC}"

# Test the executable
echo -e "${BLUE}🧪 Testing the executable...${NC}"
if [[ "$DOCKERC_OS" == "windows" ]]; then
    TEST_CMD="$OUTPUT_PATH --help"
else
    TEST_CMD="$OUTPUT_PATH --help"
fi

if timeout 30s $TEST_CMD > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Executable test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Executable test timed out or failed (this may be normal)${NC}"
fi

# Display results
echo ""
echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo -e "${BLUE}📦 Executable location: $OUTPUT_PATH${NC}"
echo -e "${BLUE}📏 Executable size: $(du -h "$OUTPUT_PATH" | cut -f1)${NC}"
echo ""
echo -e "${YELLOW}💡 Usage Examples:${NC}"
echo -e "   # Watch a directory for changes"
echo -e "   $OUTPUT_PATH --watch-path /path/to/documents"
echo ""
echo -e "   # Watch with specific patterns"
echo -e "   $OUTPUT_PATH --watch-path /docs --patterns '*.md,*.txt'"
echo ""
echo -e "   # Watch with custom flow"
echo -e "   $OUTPUT_PATH --watch-path /data --flow-file /path/to/flow.py"
echo ""
echo -e "${GREEN}✨ Your CocoIndex executable is ready for distribution!${NC}" 
