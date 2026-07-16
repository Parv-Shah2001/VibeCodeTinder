#!/bin/bash
# One-command local runner – no Docker, no K8s, just Python + Node
# Usage: ./scripts/run_local.sh

set -e

echo "🔥 VibeCodeTinder – Local Runner (No Docker/K8s)"

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "❌ python3 not found"
  exit 1
fi

# Check Node
if ! command -v npm &> /dev/null; then
  echo "❌ npm not found – please install Node 18+"
  exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "  Created .venv"
fi

source .venv/bin/activate
pip install -q -r requirements.txt
pip install -q faker || true

# Env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "  Created .env from .env.example (SQLite local)"
fi

# Storage dirs
mkdir -p storage/profile storage/message

# Seed if DB empty
if [ ! -f "vibe.db" ]; then
  echo "🌱 First run – seeding 100 demo users..."
  # Start API in background to init DB, then seed
  uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  API_PID=$!
  sleep 4
  python scripts/seed.py --count 100 || true
  kill $API_PID
  sleep 1
  echo "  Seed done – login user1@vibe.test / password123"
else
  echo "  DB exists (vibe.db) – skipping seed. Delete vibe.db to reseed."
fi

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
npm install --silent > /dev/null 2>&1 || npm install
cd ..

# Run both
echo ""
echo "🚀 Starting backend at http://localhost:8000/docs"
echo "🚀 Starting frontend at http://localhost:5173"
echo ""
echo "Login: user1@vibe.test / password123"
echo ""
echo "Press Ctrl+C to stop both"
echo ""

# Trap to kill both on exit
trap "kill 0" EXIT

# Start backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd ..

wait
