#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        host=os.environ.get('DB_HOST','db'),
        port=os.environ.get('DB_PORT','5432'),
        dbname=os.environ.get('DB_NAME','travel_ai'),
        user=os.environ.get('DB_USER','admin'),
        password=os.environ.get('DB_PASSWORD','admin'),
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
  echo "  DB not ready, retrying in 2s..."
  sleep 2
done

echo "✅ PostgreSQL is ready"
echo "📦 Running migrations..."
python manage.py migrate --noinput

# If extra arguments were passed (e.g. from docker-compose command:), run those instead of gunicorn
if [ "$#" -gt 0 ]; then
  echo "🚀 Executing: $*"
  exec "$@"
else
  echo "🚀 Starting Gunicorn..."
  exec gunicorn \
    --bind 0.0.0.0:8000 \
    --timeout 600 \
    --workers 2 \
    --access-logfile - \
    travel_ai_backend.wsgi:application
fi
