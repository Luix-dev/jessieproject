#!/bin/bash
# Wait for Postgres to start
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Initialize DB and create tables
echo "Initializing database..."
python init_db.py

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn -w 4 -b :8000 app:app
