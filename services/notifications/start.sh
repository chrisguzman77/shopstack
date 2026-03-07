#!/bin/sh
set -e

echo "Running Notifications migrations..."
alembic upgrade head

echo "Starting Notifications worker..."
exec python -m notifications_service.worker