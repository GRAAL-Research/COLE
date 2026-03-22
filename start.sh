#!/bin/sh
# Start FastAPI
echo 'Starting backend...'
uvicorn src.backend.submission_api:app \
  --host 0.0.0.0 --port 8000 --log-level debug \
  > /app/backend.log 2>&1 &

until curl -s http://localhost:8000/ > /dev/null; do
    echo "FastAPI not ready yet. Retrying in 5 seconds..."
    sleep 5
done

echo 'Backend ready'
# Start Next.js
echo 'Starting frontend...'
cd frontend
npm run start -- -p 8001 &

until curl -s http://localhost:8001/ > /dev/null 2>&1; do
    echo "Frontend not ready yet. Retrying in 3 seconds..."
    sleep 3
done

echo 'Frontend ready'
cd ..
# Start Nginx to reverse proxy (runs in foreground)
echo "Starting Nginx"
nginx -g "daemon off;"
