#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/mnt/s/urumi"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_PY="$BACKEND_DIR/.venv/bin/python"
LOG_DIR="/tmp/urumi"

mkdir -p "$LOG_DIR"

if [ ! -x "$VENV_PY" ]; then
  printf "Missing venv python at %s\n" "$VENV_PY"
  exit 1
fi

printf "Starting backend services...\n"

if ! command -v kubectl >/dev/null 2>&1; then
  printf "Warning: kubectl not found; provisioning will fail.\n"
else
  if ! kubectl cluster-info >/dev/null 2>&1; then
    printf "Warning: kubectl cluster not reachable.\n"
  fi
fi

if ! command -v helm >/dev/null 2>&1; then
  printf "Warning: helm not found; provisioning will fail.\n"
fi

cd "$BACKEND_DIR"

nohup "$VENV_PY" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info \
  > "$LOG_DIR/uvicorn.log" 2>&1 &
echo $! > "$LOG_DIR/uvicorn.pid"

nohup "$VENV_PY" -m celery -A app.tasks.celery_app.celery_app worker -l info \
  > "$LOG_DIR/celery.log" 2>&1 &
echo $! > "$LOG_DIR/celery.pid"

printf "Backend started. Logs: %s/uvicorn.log, %s/celery.log\n" "$LOG_DIR" "$LOG_DIR"

if [ "${START_FRONTEND:-0}" = "1" ]; then
  if [ -d "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"
    if command -v npm >/dev/null 2>&1; then
      nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
      echo $! > "$LOG_DIR/frontend.pid"
      printf "Frontend started. Log: %s/frontend.log\n" "$LOG_DIR"
    else
      printf "Warning: npm not found; frontend not started.\n"
    fi
  fi
fi

printf "Done.\n"
