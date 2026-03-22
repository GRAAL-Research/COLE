# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Final image with backend + built frontend
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (nginx, curl, Node.js runtime for Next.js)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    netcat-openbsd \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/docker_requirements.txt /app/src/
RUN pip install --no-cache-dir --upgrade pip wheel \
    && pip install --no-cache-dir --prefer-binary pyarrow pandas numpy scipy fsspec aiohttp tqdm \
    && pip install --no-cache-dir --prefer-binary -r /app/src/docker_requirements.txt

# Copy backend source
COPY src/ /app/src/

# Copy built frontend from stage 1
COPY --from=frontend-build /app/frontend /app/frontend

# Copy config files
COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Create non-root user and set permissions
RUN useradd -m -u 1000 user \
    && mkdir -p /app/.cache /var/lib/nginx /var/log/nginx /app/logs /run \
    && touch /run/nginx.pid \
    && chown -R user:user /app /var/lib/nginx /var/log/nginx /run

ENV HF_HOME=/app/.cache \
    HF_DATASETS_CACHE=/app/.cache

USER user
EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

CMD ["sh", "/start.sh"]
