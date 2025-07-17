# Build frontend
FROM node:18 as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.12-slim
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 user

# Copy backend code
COPY src/ ./src/

# Install PyTorch
RUN pip install -r ./src/requirements.txt

# Create and configure cache directory
RUN mkdir -p /app/.cache && \
    chown -R user:user /app


COPY --from=frontend-build /app/frontend /app/frontend

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*


# Environment variables
ENV HF_HOME=/app/.cache \
    HF_DATASETS_CACHE=/app/.cache \
    INTERNAL_API_PORT=7861 \
    PORT=7860 \
    NODE_ENV=production

COPY --from=frontend-build /app/frontend /app/frontend
# Note: HF_TOKEN should be provided at runtime, not build time
USER user
EXPOSE 7860

# Start both servers with wait-for
CMD ["sh", "-c","ls && cd frontend && ls && cd .. echo '🔧 Starting backend...' && uvicorn src.backend.submission_api:app --host 0.0.0.0 --port 7860 "]
