#!/usr/bin/env bash
# Render start script

set -o errexit  # exit on error

echo "Running database migrations..."
alembic upgrade head

echo "Starting BookIt API server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT