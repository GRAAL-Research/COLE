#!/bin/sh
# Start FastAPI
echo '🔧 Starting backend...'
uvicorn src.backend.submission_api:app --host 0.0.0.0 --port 8000  &
echo '✅ Backend ready'
ls
# Start Next.js
echo '🚀 Starting frontend'
cd /app/frontend
npm run start -- -p 8001 &
echo '🚀 Frontend ready'
# Start Nginx to reverse proxy
echo "Starting Nginx"
nginx -g "daemon off;"
echo "Nginx ready"

echo " container ready !"