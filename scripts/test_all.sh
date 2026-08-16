#!/usr/bin/env bash
# Jalankan seluruh test backend (unittest).
set -e
cd "$(dirname "$0")/../backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -q -e .
else
  . .venv/bin/activate
fi
exec python -m unittest discover -s tests -v
