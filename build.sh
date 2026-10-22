#!/usr/bin/env bash
# Script tự động build & deploy cho các nền tảng Cloud (Render, Railway, Fly.io, v.v.)
set -o errexit

echo "📦 Đang cài đặt thư viện..."
pip install -r requirements.txt

echo "🎨 Đang gom static files (CSS, JS, Fonts)..."
python manage.py collectstatic --noinput

echo "🗄️ Đang thực thi migrations CSDL..."
python manage.py migrate

echo "📖 Khởi tạo 73 cuốn Kinh Thánh và kế hoạch 365 ngày..."
python manage.py init_canon

echo "✍️ Nạp dữ liệu văn bản mẫu..."
python manage.py import_sample

echo "👤 Khởi tạo tài khoản test (admin & docgia)..."
python manage.py create_test_user

echo "✅ Hoàn tất build! Hệ thống đã sẵn sàng phục vụ."
