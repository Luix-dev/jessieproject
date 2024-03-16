#!/bin/bash
# Wait for Postgres to start
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Initialize DB and create tables
python init_db.py

# Start Gunicorn
exec gunicorn -w 4 -b :8000 app:app
