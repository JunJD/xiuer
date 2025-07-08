#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
echo "Running database migrations..."
uv run alembic upgrade head

# Start the application using uvicorn
echo "Starting application..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 