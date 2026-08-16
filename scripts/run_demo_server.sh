#!/usr/bin/env bash
# Jalankan backend FastAPI untuk sesi demo (host 0.0.0.0) dan seed data contoh demo secara otomatis.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
  echo "Membuat venv & install deps..."
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -q -e .
else
  . .venv/bin/activate
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "================================================================="
echo "  🚀 MEMULAI SERVER DEMO RENTI (Host: $HOST, Port: $PORT)"
echo "================================================================="

# Jalankan uvicorn di background
uvicorn app.main:app --host "$HOST" --port "$PORT" &
UVICORN_PID=$!

cleanup() {
  echo ""
  echo "🛑 Menghentikan server demo (PID $UVICORN_PID)..."
  kill "$UVICORN_PID" 2>/dev/null || true
  wait "$UVICORN_PID" 2>/dev/null || true
  echo "✅ Server demo berhenti."
}

trap cleanup INT TERM EXIT

# Tunggu server siap menerima request
echo "Menunggu server siap..."
READY=0
for i in $(seq 1 30); do
  if python3 -c "
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:$PORT/health', timeout=1) as resp:
        if resp.status == 200:
            exit(0)
except Exception:
    exit(1)
" 2>/dev/null; then
    READY=1
    break
  fi
  sleep 0.5
done

if [ "$READY" -ne 1 ]; then
  echo "❌ Server tidak merespon dalam batas waktu."
  exit 1
fi

echo "✅ Server siap menerima koneksi."
echo ""

# Jalankan seeding data demo melalui API
echo "🌱 Menjalankan seeding data demo (user: demo-user-001)..."
python3 "$ROOT_DIR/scripts/seed_demo_data.py" --base-url "http://127.0.0.1:$PORT"

echo ""
echo "================================================================="
echo "  📱 INFORMASI KONEKSI DEMO & MOBILE TESTING"
echo "================================================================="
python3 -c "
import socket
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'
lan_ip = get_ip()
print(f'  • Akses Lokal:     http://localhost:$PORT')
print(f'  • Akses Handphone: http://{lan_ip}:$PORT (satu jaringan Wi-Fi)')
print(f'  • Swagger Docs:    http://{lan_ip}:$PORT/docs')
"
echo "  • User Demo:       demo-user-001"
echo "================================================================="
echo "Server demo aktif. Tekan Ctrl+C untuk menghentikan server."
echo ""

# Tunggu proses uvicorn
wait "$UVICORN_PID"
