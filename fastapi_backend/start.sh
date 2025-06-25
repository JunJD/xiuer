#!/bin/bash

# Run database migrations only if AUTO_MIGRATE environment variable is set
if [ "$AUTO_MIGRATE" = "true" ]; then
    echo "Running database migrations..."
    uv run alembic upgrade head
fi

if [ -f /.dockerenv ]; then
    echo "Running in Docker"
    uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000 --reload &
    uv run python watcher.py
else
    echo "Running locally with uv"
    uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000 --reload &
    uv run python watcher.py
fi

wait
