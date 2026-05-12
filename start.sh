#!/bin/bash
set -e

echo "=== MauriGuide AI startup ==="

# ── Django setup ─────────────────────────────────────────────
echo ">>> Running Django migrations..."
cd /opt/render/project/src/backend/django_app
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo ">>> Starting Django on port 8000..."
gunicorn mauriguide.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --daemon \
  --log-file /tmp/django.log

# ── FastAPI setup ─────────────────────────────────────────────
echo ">>> Starting FastAPI on port 8001..."
cd /opt/render/project/src/backend/fastapi_app
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 1 &

# ── Nginx-style: Render only exposes one port ($PORT) ─────────
# We use a simple Python proxy to route traffic
echo ">>> Starting proxy on port $PORT..."
cd /opt/render/project/src/
python proxy.py