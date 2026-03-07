#!/bin/sh
set -e

echo "Running Auth migrations..."
alembic upgrade head

echo "Starting Auth service..."
exec uvicorn auth_service.api:app --host 0.0.0.0 --port 8001