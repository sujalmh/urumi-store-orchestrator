#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/tmp/urumi"

stop_pid() {
  local name="$1"
  local pid_file="$LOG_DIR/$name.pid"
  if [ -f "$pid_file" ]; then
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      sleep 2
      if kill -0 "$pid" >/dev/null 2>&1; then
        kill -9 "$pid" >/dev/null 2>&1 || true
      fi
      printf "Stopped %s (pid %s)\n" "$name" "$pid"
    else
      printf "%s pid not running: %s\n" "$name" "$pid"
    fi
    rm -f "$pid_file"
  else
    printf "%s pid file not found\n" "$name"
  fi
}

stop_pid "uvicorn"
stop_pid "celery"
stop_pid "frontend"

# Fallback: kill any stray processes by pattern
pkill -f "uvicorn app.main:app" >/dev/null 2>&1 || true
pkill -f "celery -A app.tasks.celery_app.celery_app worker" >/dev/null 2>&1 || true
pkill -f "npm run dev" >/dev/null 2>&1 || true
pkill -f "next dev" >/dev/null 2>&1 || true

printf "Done.\n"
