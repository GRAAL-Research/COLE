#!/bin/sh

# Start FastAPI
echo '🔧 Starting backend...'
uvicorn src.backend.submission_api:app --host 0.0.0.0 --port 8000 > /app/backend.log 2>&1 &
echo '✅ Backend ready'

# Start Next.js
echo '🚀 Starting frontend'
cd /app/frontend
npm run start -- -p 8001 > /app/frontend.log 2>&1 &
echo '🚀 Frontend ready'
# Start Nginx to reverse proxy
echo "Starting Nginx"
nginx -g "daemon off;"
echo "Nginx ready"

echo " container ready !"