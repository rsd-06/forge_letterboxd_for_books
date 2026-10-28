#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
python3 -m pip install -r requirements.txt

echo "=== Collecting Static Files ==="
python3 manage.py collectstatic --noinput --clear

echo "=== Copying Media Assets ==="
mkdir -p staticfiles_build/media
if [ -d "media" ]; then
    cp -r media/* staticfiles_build/media/ || true
fi

if [ -n "$DATABASE_URL" ]; then
    echo "=== Running Database Migrations ==="
    python3 manage.py migrate --noinput
    echo "=== Populating Demo Data ==="
    python3 manage.py seed_books
fi

echo "=== Vercel Build Completed Successfully ==="
