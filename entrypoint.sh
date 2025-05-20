#!/bin/bash

# Wait for database to be ready
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == *"postgres"* ]]; then
  echo "Waiting for postgres..."
  
  # Extract host and port from DATABASE_URL
  # Example: postgres://user:password@db:5432/dbname
  DB_HOST=$(echo $DATABASE_URL | awk -F@ '{ print $2 }' | awk -F: '{ print $1 }' | awk -F/ '{ print $1 }')
  DB_PORT=$(echo $DATABASE_URL | awk -F: '{ print $4 }' | awk -F/ '{ print $1 }')
  
  # If port isn't specified, use default PostgreSQL port
  if [ -z "$DB_PORT" ]; then
    DB_PORT=5432
  fi
  
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  
  # Try to connect to PostgreSQL
  until nc -z "$DB_HOST" "$DB_PORT"; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done
  
  echo "PostgreSQL started"
else
  echo "Using SQLite or another database, skipping connection check"
fi

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear

# Execute the command passed to docker
exec "$@" 