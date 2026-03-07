#!/bin/sh
set -e

echo "Running Orders migrations..."
alembic upgrade head

echo "Starting Orders service..."
exec uvicorn orders_service.api:app --host 0.0.0.0 --port 8002