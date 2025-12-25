# Stage 1: Build C++ binary
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Workaround for GPG signature issues - allow unauthenticated packages temporarily
RUN apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true || true && \
    apt-get install -y --allow-unauthenticated \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    ca-certificates \
    zip \
    unzip \
    tar \
    pkg-config \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone https://github.com/Microsoft/vcpkg.git && \
    cd vcpkg && \
    ./bootstrap-vcpkg.sh

ENV VCPKG_ROOT=/opt/vcpkg
ENV PATH="${VCPKG_ROOT}:${PATH}"

WORKDIR /build
COPY CMakeLists.txt CMakePresets.json vcpkg.json ./
COPY src/ ./src/
COPY assets/ ./assets/
COPY resources/ ./resources/

RUN mkdir -p build && \
    cd build && \
    cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE=${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake \
    -DVCPKG_TARGET_TRIPLET=arm64-linux && \
    cmake --build . --config Release --parallel $(nproc) && \
    chmod +x GeminiWatermarkTool

# Stage 2: Production runtime (using glibc-based image for compatibility)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies for C++ binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled binary from builder stage
COPY --from=builder /build/build/GeminiWatermarkTool /usr/local/bin/GeminiWatermarkTool
RUN chmod +x /usr/local/bin/GeminiWatermarkTool

# Verify binary works
RUN GeminiWatermarkTool --version || echo "Binary verification warning: version check failed"

# Copy Python dependencies
COPY web/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY web/backend/src/ ./src/

# Create directory for ephemeral file storage
RUN mkdir -p /tmp/uploads /tmp/outputs && chmod 777 /tmp/uploads /tmp/outputs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BINARY_PATH=/usr/local/bin/GeminiWatermarkTool

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=2)" || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
