#!/usr/bin/env bash
# Jalankan backend FastAPI selama pengembangan.
set -e
cd "$(dirname "$0")/../backend"
if [ ! -d ".venv" ]; then
  echo "Membuat venv & install deps..."
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -q -e .
else
  . .venv/bin/activate
fi
exec uvicorn app.main:app --reload --port 8000
