#!/bin/bash
# Entrypoint script for Docker container

set -e

# Wait for postgres to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U giftpulse; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Execute the main command
exec "$@"
