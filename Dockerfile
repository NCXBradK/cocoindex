# Use the official uv Python base image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Install system dependencies for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
        curl \
        pkg-config \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain via rustup (for 2024 edition support)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY examples/ ./examples/
COPY python/ ./python/
COPY src/ ./src/
COPY Cargo.toml ./
COPY Cargo.lock ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies into the virtual environment
RUN uv pip install --no-cache-dir \
    qdrant-client \
    neo4j \
    watchdog \
    fire \
    psycopg2-binary \
    && uv pip install --no-cache-dir -e .

# Production stage
FROM python:3.12-slim-bookworm AS production

# Install runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY examples/ ./examples/
COPY python/ ./python/
COPY watch_and_index.py ./
COPY start_mcp_server.sh ./
COPY entrypoint.sh ./

# Make scripts executable
RUN chmod +x start_mcp_server.sh entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["python", "watch_and_index.py"] 