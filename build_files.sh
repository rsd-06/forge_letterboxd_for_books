#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
if command -v uv &> /dev/null; then
    echo "Detected uv, installing dependencies..."
    uv pip install --system -r requirements.txt || python3 -m pip install -r requirements.txt --break-system-packages
else
    echo "Using pip with --break-system-packages..."
    python3 -m pip install -r requirements.txt --break-system-packages 2>/dev/null || python3 -m pip install -r requirements.txt
fi

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
