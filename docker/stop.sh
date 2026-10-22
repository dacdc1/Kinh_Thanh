#!/usr/bin/env bash
# ==============================================================================
# Script Dừng Hệ Thống Docker Compose
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "🛑 Đang dừng toàn bộ các containers..."
docker compose down
echo "✅ Đã dừng hệ thống an toàn."
