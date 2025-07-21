# Build frontend
FROM node:18 as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.12-slim as backend
WORKDIR /app

# Install dependencies including nginx
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt /app/src/
RUN pip install torch
RUN pip install -r /app/src/requirements.txt
COPY src/ /app/src/

# Copy Nginx config (adjust path if needed)
COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=frontend-build /app/frontend /app/frontend

# Create non-root user
RUN useradd -m -u 1000 user

# Create and configure cache directory
RUN mkdir -p /app/.cache && \
    chown -R user:user /app

# Environment variables
ENV HF_HOME=/app/.cache \
    HF_DATASETS_CACHE=/app/.cache \
    INTERNAL_API_PORT=7861 \
    PORT=7860

WORKDIR /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh /start.sh
RUN chmod +x /start.sh
RUN chown -R user:user /var/lib/nginx

RUN apt-get update && apt-get install -y nginx \
    && groupadd -r nginx && useradd -r -g nginx nginx

#Give user nginx write permissions
RUN mkdir -p /var/lib/nginx && chown -R user:user /var/lib/nginx
RUN mkdir -p /var/log/nginx && chown -R user:user /var/log/nginx
RUN mkdir -p /app/logs && chown -R user:user /app/logs
RUN mkdir -p /run && touch /run/nginx.pid && chown -R user:user /run

RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*


# Note: HF_TOKEN should be provided at runtime, not build time
USER user
EXPOSE 7860

# Start both servers with wait-for
CMD ["sh", "/start.sh"]