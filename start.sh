#!/bin/bash
# Tender Portal - Startup Script
set -e

cd "$(dirname "$0")"

echo "=== Tender Portal ==="

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Starting PostgreSQL and Redis..."
    docker compose up -d
    sleep 3
else
    echo "Docker not found. Please ensure PostgreSQL and Redis are running."
    echo "  PostgreSQL: localhost:5432 (user: tender_user, pass: tender_pass, db: tender_db)"
    echo "  Redis: localhost:6379"
fi

# Start Backend
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "Starting frontend dev server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== Services Started ==="
echo "  Backend API: http://localhost:8000"
echo "  Frontend:    http://localhost:5173"
echo "  API Docs:    http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
