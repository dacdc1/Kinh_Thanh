#!/usr/bin/env bash
# ==============================================================================
# Script Khởi Động & Deploy Kinh Thánh Công Giáo qua Cloudflare Tunnel
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# 1. Kích hoạt môi trường ảo
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "=================================================================="
echo "🕊️  KHỞI ĐỘNG HỆ THỐNG KINH THÁNH CÔNG GIÁO QUA CLOUDFLARE TUNNEL"
echo "=================================================================="

# 2. Chuẩn bị Cơ sở dữ liệu và Static Files
echo "📦 1. Đang kiểm tra CSDL và nạp dữ liệu..."
python manage.py migrate --noinput
python manage.py init_canon
python manage.py import_sample
python manage.py create_test_user
python manage.py collectstatic --noinput > /dev/null 2>&1

# 3. Dọn dẹp process cũ nếu còn chạy trên port 8000
echo "🧹 2. Đang kiểm tra cổng 8000..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true

# 4. Khởi động Gunicorn WSGI Server ở chế độ nền
echo "🚀 3. Đang khởi động Gunicorn Production Server (127.0.0.1:8000)..."
gunicorn kinhthanh_project.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile - \
    --daemon

sleep 2

# Kiểm tra Gunicorn đã sống chưa
if ! curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "❌ Lỗi: Gunicorn chưa thể khởi động. Vui lòng kiểm tra lại cấu hình."
    exit 1
fi
echo "✅ Gunicorn đang chạy ổn định tại http://127.0.0.1:8000"

# 5. Khởi chạy Cloudflare Tunnel
echo "🌐 4. Đang kết nối mạng toàn cầu Cloudflare Tunnel..."
echo "------------------------------------------------------------------"
echo "Đang tạo đường dẫn HTTPS công khai an toàn (Cloudflare Edge)..."
echo "URL truy cập sẽ hiển thị bên dưới (kết thúc bằng .trycloudflare.com):"
echo "------------------------------------------------------------------"

if [ -f ".venv/bin/cloudflared" ]; then
    CLOUDFLARED_BIN=".venv/bin/cloudflared"
else
    CLOUDFLARED_BIN="cloudflared"
fi

exec "$CLOUDFLARED_BIN" tunnel --url http://127.0.0.1:8000
