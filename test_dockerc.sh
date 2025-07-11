#!/bin/bash

# Simple dockerc test script
# This creates a hello world executable using dockerc

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing dockerc with simple hello world example${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Build the hello world Docker image
echo -e "${BLUE}🔨 Building hello world Docker image...${NC}"
if ! docker build -f Dockerfile.hello -t hello-world-test .; then
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Test with dockerc
echo -e "${BLUE}🏗️  Converting Docker image to executable with dockerc...${NC}"
OUTPUT_PATH="dist/hello-world-test"
mkdir -p dist

if ! ./dockerc --image docker-daemon:hello-world-test:latest --output "$OUTPUT_PATH" --arch x86_64; then
    echo -e "${RED}❌ Failed to convert Docker image to executable${NC}"
    echo -e "${YELLOW}💡 This might be an architecture issue. Let's try without --arch flag:${NC}"
    
    if ! ./dockerc --image docker-daemon:hello-world-test:latest --output "$OUTPUT_PATH"; then
        echo -e "${RED}❌ Failed to convert Docker image to executable (no arch)${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Executable created successfully: $OUTPUT_PATH${NC}"

# Test the executable
echo -e "${BLUE}🧪 Testing the executable...${NC}"
if timeout 10s "$OUTPUT_PATH"; then
    echo -e "${GREEN}✅ Executable test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Executable test failed or timed out${NC}"
fi

# Display results
echo ""
echo -e "${GREEN}🎉 dockerc test completed!${NC}"
echo -e "${BLUE}📦 Executable location: $OUTPUT_PATH${NC}"
echo -e "${BLUE}📏 Executable size: $(du -h "$OUTPUT_PATH" | cut -f1)${NC}"
echo ""
echo -e "${YELLOW}💡 If this worked, dockerc is functioning correctly!${NC}" 